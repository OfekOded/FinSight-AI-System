import uuid
import requests
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from schemas import (
    TransactionCreate,
    TransactionResponse,
    DashboardData,
    AIQueryRequest,
    AIQueryResponse
)
from database import engine, Base, get_db
from models import Event

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinSight AI Backend System")

def get_exchange_rate(from_currency: str, to_currency: str = "ILS") -> float:
    if from_currency == "ILS":
        return 1.0
    
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url)
        data = response.json()
        return data["rates"].get(to_currency, 1.0)
    except Exception:
        return 1.0

@app.get("/")
def read_root():
    return {"message": "FinSight System is online", "version": "1.0.0"}

@app.post("/api/transactions", response_model=TransactionResponse)
def add_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    rate = get_exchange_rate(transaction.currency)
    final_amount_ils = transaction.amount * rate

    new_id = str(uuid.uuid4())
    
    response_obj = {
        "id": new_id,
        "status": "confirmed",
        "amount_in_ils": final_amount_ils,
        **transaction.dict()
    }

    new_event = Event(
        aggregate_id=new_id,
        event_type="TransactionCreated",
        payload=response_obj
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return response_obj

@app.get("/api/dashboard", response_model=DashboardData)
def get_dashboard_data(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    
    transactions = []
    total_spent = 0.0
    
    for event in events:
        if event.event_type == "TransactionCreated":
            data = event.payload
            transactions.append(data)
            total_spent += data["amount_in_ils"]
            
    return {
        "total_balance": 20000.0 - total_spent,
        "monthly_expenses": total_spent,
        "recent_transactions": transactions[-5:]
    }

@app.post("/api/ai/consult", response_model=AIQueryResponse)
def consult_ai_agent(query: AIQueryRequest):
    return {
        "answer": f"Analysis based on your data: '{query.question}' is a valid concern. Spending trend is stable.",
        "suggested_action": "Review Subscription Costs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)