import json
from pydantic import BaseModel
from typing import List
from ollama import AsyncClient

class AIResult(BaseModel):
    answer: str
    suggested_action: str

async def get_financial_advice(question: str, history: List, user_context: dict) -> dict:
    system_prompt = f"""You are a smart financial advisor for the FinSight app. Answer in Hebrew.
User Profile:
Name: {user_context['name']}
Salary: {user_context['salary']}
Budgets: {json.dumps(user_context['budgets'], ensure_ascii=False)}
Subscriptions: {json.dumps(user_context['subscriptions'], ensure_ascii=False)}
Savings Goals: {json.dumps(user_context['savings'], ensure_ascii=False)}
Recent Transactions: {json.dumps(user_context['recent_transactions'], ensure_ascii=False)}

You must return ONLY a valid JSON object with exactly two keys: "answer" and "suggested_action". Do not include markdown or explanations outside the JSON."""

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
        
    messages.append({"role": "user", "content": question})

    try:
        response = await AsyncClient().chat(
            model='llama3',
            messages=messages,
            format='json',
            options={"temperature": 0.3}
        )
        
        raw_text = response['message']['content'].strip()
        return json.loads(raw_text)
    except Exception as e:
        return {"answer": str(e), "suggested_action": ""}

async def analyze_receipt_image(image_bytes: bytes) -> dict:
    try:
        prompt = "Analyze this receipt image and extract the following details into a pure JSON object. Keys required: merchant, amount, date, category. Output ONLY the JSON object."
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
        return {"merchant": "שגיאת פענוח", "amount": 0, "category": "אחר", "error": str(e)}