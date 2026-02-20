import json
from pydantic import BaseModel, Field
from typing import List
from ollama import AsyncClient
from dotenv import load_dotenv
import os
from huggingface_hub import AsyncInferenceClient
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

token = os.getenv("HF_TOKEN")
hf_client = AsyncInferenceClient(token=token)

class AIResultFormat(BaseModel):
    response: str = Field(description="The financial advice response in Hebrew")
    suggested_action: str = Field(description="A short, actionable recommendation in Hebrew")

async def analyze_sentiment(text: str) -> str:
    try:
        result = await hf_client.text_classification(text)
        if result:
            print(result[0]['label'])
            return result[0]['label']
        return "neutral"
    except Exception:
        return "neutral"

async def get_mcp_context() -> str:
    server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    server_params = StdioServerParameters(command="python", args=[server_path])
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("get_financial_context", arguments={})
                return result.content[0].text
    except Exception:
        return "Market data is currently unavailable."

async def get_financial_advice(question: str, history: List, user_context: dict) -> dict:
    mcp_context = await get_mcp_context()
    sentiment = await analyze_sentiment(question)
    parser = PydanticOutputParser(pydantic_object=AIResultFormat)
    
    system_prompt = f"""You are a smart financial advisor for the FinSight app.
User Profile:
Name: {user_context['name']}
Salary: {user_context['salary']}
Budgets: {json.dumps(user_context['budgets'], ensure_ascii=False)}
Subscriptions: {json.dumps(user_context['subscriptions'], ensure_ascii=False)}
Savings Goals: {json.dumps(user_context['savings'], ensure_ascii=False)}
Recent Transactions: {json.dumps(user_context['recent_transactions'], ensure_ascii=False)}

Market Context: {mcp_context}
User Sentiment: {sentiment}

You MUST output ONLY a valid JSON object. Do not output any other text.
The keys must be exactly "response" and "suggested_action".
The values MUST be strings.
{parser.get_format_instructions()}
"""

    messages = [SystemMessage(content=system_prompt)]
    recent_history = history[-4:] if history else []
    
    for msg in recent_history:
        try:
            role = msg.role if hasattr(msg, 'role') else msg.get('role')
            content = msg.content if hasattr(msg, 'content') else msg.get('content')
            if role == 'user':
                messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                messages.append(AIMessage(content=content))
        except Exception:
            continue
            
    messages.append(HumanMessage(content=question))
    llm = ChatOllama(model="llama3.1", temperature=0.1, format="json")
    
    try:
        response = await llm.ainvoke(messages)
        parsed_output = parser.invoke(response.content)
        result_dict = parsed_output.model_dump()
        return {
            "response": str(result_dict.get("response", "")),
            "suggested_action": str(result_dict.get("suggested_action", ""))
        }
    except Exception:
        try:
            raw_content = response.content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
            raw_content = raw_content.strip()

            if not raw_content.startswith('{'):
                start_idx = raw_content.find('{')
                end_idx = raw_content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    raw_content = raw_content[start_idx:end_idx]
                    
            data = json.loads(raw_content)
            
            resp_val = data.get("response", "לא הצלחתי לנסח תשובה מלאה.")
            act_val = data.get("suggested_action", "")
            
            if not isinstance(resp_val, str):
                resp_val = json.dumps(resp_val, ensure_ascii=False)
            if not isinstance(act_val, str):
                act_val = json.dumps(act_val, ensure_ascii=False)
                
            return {
                "response": resp_val, 
                "suggested_action": act_val
            }
        except Exception:
            return {"response": "אופס! נראה שיש כרגע עומס קטן. נסה לשאול שוב בעוד כמה רגעים", "suggested_action": ""}

async def analyze_receipt_image(image_bytes: bytes) -> dict:
    try:
        response = await AsyncClient().chat(
            model='llava',
            messages=[{'role': 'user', 'content': "Analyze this receipt image and extract the following details into a pure JSON object. Keys required: merchant, amount, date, category. Output ONLY the JSON object.", 'images': [image_bytes]}]
        )
        raw_text = response['message']['content'].strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        data = json.loads(raw_text.strip())
        return {"merchant": data.get("merchant", "לא זוהה"), "amount": data.get("amount", 0), "date": data.get("date"), "category": data.get("category", "כללי")}
    except Exception:
        return {"merchant": "שגיאת פענוח", "amount": 0, "category": "אחר"}