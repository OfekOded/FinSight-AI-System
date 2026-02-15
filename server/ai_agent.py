import json
import os
from pydantic import BaseModel
from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from transformers import pipeline
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

class AIResult(BaseModel):
    answer: str
    suggested_action: str

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