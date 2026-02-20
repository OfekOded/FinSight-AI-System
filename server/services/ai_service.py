from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine, Base, get_db
from models import Event, User, BudgetCategory, Subscription, SavingsGoal
from schemas import AIQueryRequest, AIQueryResponse
from services.shared import get_current_user
from ai_agent import get_financial_advice, analyze_receipt_image

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/api/receipts/analyze")
async def analyze_receipt(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400)
    try:
        contents = await file.read()
        result = await analyze_receipt_image(contents)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/consult", response_model=AIQueryResponse)
async def consult_ai_agent(query: AIQueryRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        events = db.query(Event).filter(Event.user_id == user.id, Event.event_type == "TransactionCreated").order_by(Event.timestamp.desc()).limit(15).all()
        transactions = [event.payload for event in events]
        budgets = db.query(BudgetCategory).filter(BudgetCategory.user_id == user.id).all()
        subs = db.query(Subscription).filter(Subscription.user_id == user.id).all()
        savings = db.query(SavingsGoal).filter(SavingsGoal.user_id == user.id).all()
        
        user_context = {
            "name": user.full_name or user.username,
            "salary": user.salary,
            "budgets": [{"name": b.name, "limit": b.limit_amount, "spent": b.spent_amount} for b in budgets],
            "subscriptions": [{"name": s.name, "amount": s.amount} for s in subs],
            "savings": [{"name": s.name, "target": s.target_amount, "current": s.current_amount} for s in savings],
            "recent_transactions": transactions
        }
        
        ai_result = await get_financial_advice(query.question, query.history, user_context)
        return AIQueryResponse(
            response=ai_result.get("response", ""),
            suggested_action=ai_result.get("suggested_action", "")
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)