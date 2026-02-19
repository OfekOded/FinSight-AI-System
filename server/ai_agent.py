import json
from pydantic import BaseModel
from typing import List
from ollama import AsyncClient
from dotenv import load_dotenv
import os
from huggingface_hub import AsyncInferenceClient

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

token = os.getenv("HF_TOKEN")


class AIResult(BaseModel):
    answer: str
    suggested_action: str

hf_client = AsyncInferenceClient(token=token)

# async def get_financial_advice(question: str, history: List, user_context: dict) -> dict:
#     system_prompt = f"""You are a smart financial advisor for the FinSight app. Answer in Hebrew.
# User Profile:
# Name: {user_context['name']}
# Salary: {user_context['salary']}
# Budgets: {json.dumps(user_context['budgets'], ensure_ascii=False)}
# Subscriptions: {json.dumps(user_context['subscriptions'], ensure_ascii=False)}
# Savings Goals: {json.dumps(user_context['savings'], ensure_ascii=False)}
# Recent Transactions: {json.dumps(user_context['recent_transactions'], ensure_ascii=False)}

# You must return ONLY a valid JSON object with exactly two keys: "answer" and "suggested_action". Do not include markdown or explanations outside the JSON."""

#     messages = [{"role": "system", "content": system_prompt}]
    
#     for msg in history:
#         messages.append({"role": msg.role, "content": msg.content})
        
#     messages.append({"role": "user", "content": question})

#     try:
#         response = await AsyncClient().chat(
#             model='llama3',
#             messages=messages,
#             format='json',
#             options={"temperature": 0.3}
#         )
        
#         raw_text = response['message']['content'].strip()
#         return json.loads(raw_text)
#     except Exception as e:
#         return {"answer": str(e), "suggested_action": ""}

async def get_financial_advice(question: str, history: List, user_context: dict) -> dict:
    system_prompt = f"""You are a smart financial advisor for the FinSight app. Answer in Hebrew.
User Profile:
Name: {user_context['name']}
Salary: {user_context['salary']}
Budgets: {json.dumps(user_context['budgets'], ensure_ascii=False)}
Subscriptions: {json.dumps(user_context['subscriptions'], ensure_ascii=False)}
Savings Goals: {json.dumps(user_context['savings'], ensure_ascii=False)}
Recent Transactions: {json.dumps(user_context['recent_transactions'], ensure_ascii=False)}

CRITICAL INSTRUCTIONS FOR YOUR RESPONSE:
1. You MUST output ONLY a pure, valid JSON object.
2. The JSON MUST have exactly two keys: "answer" and "suggested_action".
3. Do NOT use double quotes (") inside your text values. Use single quotes (') instead.
4. Do NOT wrap the JSON in markdown blocks (like ```json). Just return the raw {{...}}.
5. Your answer should be concise and directly address the user's question based on their financial context.
6. The "suggested_action" should be a short, actionable recommendation (e.g., "Review your subscriptions", "Consider reducing dining out expenses", "Great job! Your budget looks healthy.", etc.)
7. Always ensure the JSON is properly formatted and can be parsed without errors.
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in history:
        role = msg.role if hasattr(msg, 'role') else msg.get('role')
        content = msg.content if hasattr(msg, 'content') else msg.get('content')
        if role and content:
            messages.append({"role": role, "content": content})
        
    messages.append({"role": "user", "content": question})

    try:
        # פנייה לשרתים של Hugging Face (שימוש במודל חכם ומהיר של Llama 3)
        response = await hf_client.chat_completion(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=messages,
            temperature=0.25,
            max_tokens=800
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # מנגנון הגנה למקרה שהמודל מחזיר את ה-JSON עטוף ב-Markdown
        # 
        # if raw_text.startswith("```json"):
        #     raw_text = raw_text[7:]
        # if raw_text.startswith("```"):
        #     raw_text = raw_text[3:]
        # if raw_text.endswith("```"):
        #     raw_text = raw_text[:-3]
        
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            # חותכים רק את החלק שמתחיל ב-{ ונגמר ב-}
            json_str = raw_text[start_idx:end_idx+1]
            json_str = json_str.replace('\n', ' ')
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}. Returning raw text instead.")
                return {"answer": raw_text.replace('{', '').replace('}', '').replace('"', ''), "suggested_action": ""}
        else:
            print("No JSON structure found. Returning pure text.")
            return {"answer": raw_text, "suggested_action": ""}
        
            
    except Exception as e:
        print(f"AI Connection Error: {e}") 
        return {
            "answer": "אופס! נראה שיש כרגע עומס קטן על היועץ הפיננסי. נסה לשאול אותי שוב בעוד כמה רגעים 😅", 
            "suggested_action": ""
        }

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