import json
import os
from pydantic import BaseModel
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from transformers import pipeline
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from ollama import AsyncClient

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

class AIResult(BaseModel):
    answer: str
    suggested_action: str

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def analyze_query_intent(text: str) -> str:
    labels = ["budgeting", "investing", "saving", "general expense"]
    result = classifier(text, labels)
    return result["labels"][0]

async def get_financial_advice(question: str, transactions: List[dict]) -> dict:
    intent = analyze_query_intent(question)
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    mcp_context = ""
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                if tools:
                    result = await session.call_tool("get_financial_context", {})
                    mcp_context = str(result.content)
    except Exception:
        mcp_context = "Market data unavailable."
            
    llm = ChatOllama(model="llama3", format="json", temperature=0.3)
    context_data = json.dumps(transactions, ensure_ascii=False)
    
    prompt = PromptTemplate.from_template(
        'You are a financial advisor for FinSight app. Answer in Hebrew. '
        'User Intent: {intent}. '
        'MCP Market Context: {mcp_context}. '
        'Transactions: {context}. '
        'Question: {question}. '
        'Return a JSON object with exactly two keys: "answer" and "suggested_action".'
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "intent": intent,
        "mcp_context": mcp_context,
        "context": context_data,
        "question": question
    })
    
    try:
        return json.loads(response.content)
    except Exception:
        return {"answer": str(response.content), "suggested_action": ""}

async def analyze_receipt_image(image_bytes: bytes) -> dict:
    try:
        prompt = """
        Analyze this receipt image and extract the following details into a pure JSON object.
        Keys required:
        - merchant: Name of the business.
        - amount: Total amount (number only).
        - date: YYYY-MM-DD or null.
        - category: One of [מזון, דלק, בילויים, קניות, סופר, חשבונות, אחר].

        Output ONLY the JSON object. Do not add markdown or explanations.
        """

        response = await AsyncClient().chat(
            model='llava',
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [image_bytes]
            }]
        )

        raw_text = response['message']['content'].strip()
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        data = json.loads(raw_text.strip())
        
        return {
            "merchant": data.get("merchant", "לא זוהה"),
            "amount": data.get("amount", 0),
            "date": data.get("date"),
            "category": data.get("category", "כללי")
        }

    except Exception as e:
        print(f"Ollama Vision Error: {e}")
        return {
            "merchant": "שגיאת פענוח",
            "amount": 0,
            "category": "אחר",
            "error": str(e)
        }