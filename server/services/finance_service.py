import uuid
import requests
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine, Base, get_db
from models import Event, User, BudgetCategory, Subscription, SavingsGoal
from schemas import TransactionCreate, TransactionResponse, DashboardData, BudgetCategoryCreate, SavingsGoalCreate, SubscriptionCreate, BudgetDataResponse
from services.shared import get_current_user
from projectors import dispatch_event

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_exchange_rate(from_currency: str, to_currency: str = "ILS") -> float:
    if from_currency == "ILS": return 1.0
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url)
        return response.json()["rates"].get(to_currency, 1.0)
    except Exception: return 1.0

@app.post("/api/transactions", response_model=TransactionResponse)
def add_transaction(transaction: TransactionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rate = get_exchange_rate(transaction.currency)
    final_amount_ils = transaction.amount * rate
    new_id = str(uuid.uuid4())
    response_obj = {
        "id": new_id,
        "user_id": user.id,
        "status": "confirmed",
        "amount_in_ils": final_amount_ils,
        **transaction.model_dump()
    }
    new_event = Event(user_id=user.id, aggregate_id=new_id, event_type="TransactionCreated", payload=response_obj)
    db.add(new_event)
    dispatch_event("TransactionCreated", response_obj, db)
    db.commit()
    return response_obj

@app.get("/api/dashboard", response_model=DashboardData)
def get_dashboard_data(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    events = db.query(Event).filter(Event.user_id == user.id, Event.event_type == "TransactionCreated").all()
    transactions = []
    total_spent = 0.0
    for event in events:
        data = event.payload
        transactions.append(data)
        total_spent += data.get("amount_in_ils", data.get("amount", 0))
    subscriptions = db.query(Subscription).filter(Subscription.user_id == user.id).all()
    subs_total = 0.0
    current_month_str = datetime.now().strftime("%Y-%m")
    for sub in subscriptions:
        amount = float(sub.amount)
        subs_total += amount
        transactions.append({
            "id": f"sub-{sub.id}-{current_month_str}",
            "title": f"{sub.name}",
            "amount": amount,
            "category": "מנויים",
            "date": f"{current_month_str}-01",
            "currency": "ILS",
            "amount_in_ils": amount,
            "status": "subscription"
        })
    transactions.sort(key=lambda x: x.get("date", ""), reverse=True)
    total_monthly_spent = total_spent + subs_total
    balance = (user.salary if user.salary else 0.0) - total_monthly_spent
    return {
        "total_balance": balance,
        "monthly_expenses": total_monthly_spent,
        "recent_transactions": transactions
    }

@app.post("/api/budget/category")
def add_budget_category(item: BudgetCategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    events = db.query(Event).filter(Event.user_id == user.id, Event.event_type == "TransactionCreated").all()
    past_spent = 0.0
    budget_name = item.name.strip()
    for event in events:
        data = event.payload
        if data.get("category", "").strip() == budget_name:
             past_spent += float(data.get("amount_in_ils", 0.0))
    new_cat = BudgetCategory(user_id=user.id, name=item.name, limit_amount=item.limit_amount, spent_amount=past_spent)
    db.add(new_cat)
    db.commit()
    return {"status": "success", "id": new_cat.id}

@app.get("/api/budget", response_model=BudgetDataResponse)
def get_budget_data(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    budgets = db.query(BudgetCategory).filter(BudgetCategory.user_id == user.id).all()
    subs = db.query(Subscription).filter(Subscription.user_id == user.id).all()
    savings = db.query(SavingsGoal).filter(SavingsGoal.user_id == user.id).all()
    return {"budgets": budgets, "subscriptions": subs, "savings": savings}

@app.put("/api/budget/savings/{goal_id}/deposit")
def deposit_to_savings(goal_id: int, amount: float = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404)
    goal.current_amount += amount
    new_id = str(uuid.uuid4())
    transaction_payload = {
        "id": new_id,
        "user_id": user.id,
        "title": f"{goal.name}", 
        "amount": amount,
        "amount_in_ils": amount,
        "category": "חיסכון",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "currency": "ILS",
        "status": "confirmed"
    }
    new_event = Event(user_id=user.id, aggregate_id=new_id, event_type="TransactionCreated", payload=transaction_payload)
    db.add(new_event)
    db.commit()
    return {"status": "success", "new_amount": goal.current_amount}

@app.delete("/api/budget/savings/{goal_id}")
def delete_savings_goal(goal_id: int, refund: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404)
    if refund and goal.current_amount > 0:
        new_id = str(uuid.uuid4())
        transaction_payload = {
            "id": new_id,
            "user_id": user.id,
            "title": f"{goal.name}",
            "amount": -goal.current_amount,
            "amount_in_ils": -goal.current_amount,
            "category": "החזר",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "currency": "ILS",
            "status": "confirmed"
        }
        new_event = Event(user_id=user.id, aggregate_id=new_id, event_type="TransactionCreated", payload=transaction_payload)
        db.add(new_event)
    db.delete(goal)
    db.commit()
    return {"status": "deleted"}

@app.post("/api/budget/savings")
def add_savings_goal(goal: SavingsGoalCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    new_goal = SavingsGoal(user_id=user.id, name=goal.name, target_amount=goal.target, current_amount=goal.current)
    db.add(new_goal)
    db.commit()
    return {"status": "success", "id": new_goal.id}

@app.post("/api/budget/subscription")
def add_subscription(item: SubscriptionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    new_sub = Subscription(user_id=user.id, name=item.name, amount=item.amount)
    db.add(new_sub)
    db.commit()
    return {"status": "success", "id": new_sub.id}

@app.delete("/api/budget/subscription/{sub_id}")
def delete_subscription(sub_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sub = db.query(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == user.id).first()
    if not sub:
        raise HTTPException(status_code=404)
    db.delete(sub)
    db.commit()
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)