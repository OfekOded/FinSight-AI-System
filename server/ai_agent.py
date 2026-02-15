import json
import google.generativeai as genai
from pydantic import BaseModel
from typing import List

genai.configure(api_key="AIzaSyBwUmMt8zLEPmxlA6yWA99vl1JE5Yz8jR0")

class AIResult(BaseModel):
    answer: str
    suggested_action: str

def get_financial_advice(question: str, transactions: List[dict]) -> dict:
    model = genai.GenerativeModel("gemini-2.5-flash")
    context = json.dumps(transactions, ensure_ascii=False)
    
    prompt = f"""
    אתה יועץ פיננסי אישי וחכם של אפליקציית FinSight.
    הנה היסטוריית העסקאות של המשתמש בפורמט JSON:
    {context}
    
    שאלת המשתמש: {question}
    
    ענה למשתמש בשפה טבעית, ברורה ובעברית בלבד בהתבסס על הנתונים.
    החזר אובייקט JSON הכולל את המפתחות הבאים:
    1. "answer" - התשובה הפיננסית המפורטת שלך למשתמש.
    2. "suggested_action" - שאלת המשך קצרה, נפוצה או פעולה מומלצת שתוצג ככפתור בסוף התשובה.
    """
    
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=AIResult
        )
    )
    
    return json.loads(response.text)