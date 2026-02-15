import uuid
import requests
import hashlib
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ai_agent import get_financial_advice

from schemas import (
    TransactionCreate,
    TransactionResponse,
    DashboardData,
    AIQueryRequest,
    AIQueryResponse,
    UserRegister,
    UserLogin,
    AuthResponse,
    BudgetSchema,
    SubscriptionSchema,
    SavingsGoalSchema,
    SavingsGoalCreate,
    BudgetDataResponse,
    BudgetCategoryCreate,
    SubscriptionCreate
)
from database import engine, Base, get_db
from models import Event, User, BudgetCategory, Subscription, SavingsGoal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinSight AI Backend System")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_exchange_rate(from_currency: str, to_currency: str = "ILS") -> float:
    if from_currency == "ILS": return 1.0
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url)
        data = response.json()
        return data["rates"].get(to_currency, 1.0)
    except Exception: return 1.0

@app.get("/")
def read_root():
    return {"message": "FinSight System is online", "version": "1.0.0"}

# --- AUTHENTICATION ---
@app.post("/api/auth/register", response_model=AuthResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username exists")
    new_user = User(username=user.username, full_name=user.full_name, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"token": f"token-{new_user.id}", "username": new_user.username, "status": "created"}

@app.post("/api/auth/login", response_model=AuthResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.password_hash != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": f"token-{db_user.id}", "username": db_user.username, "status": "logged_in"}

# --- BUSINESS LOGIC ---
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

    new_event = Event(aggregate_id=new_id, event_type="TransactionCreated", payload=response_obj)
    
    # --- תיקון: עדכון חכם דו-כיווני של התקציב ---
    # שולפים את כל התקציבים ובודקים אחד אחד
    all_budgets = db.query(BudgetCategory).all()
    trans_cat = transaction.category.strip()
    
    for cat in all_budgets:
        budget_name = cat.name.strip()
        # בדיקה: האם הקטגוריה מוכלת בתקציב או התקציב מוכל בקטגוריה
        if trans_cat and (trans_cat in budget_name or budget_name in trans_cat):
            cat.spent_amount += final_amount_ils
            # הערה: אפשר להוסיף break אם רוצים לשייך רק לתקציב אחד, 
            # אבל כרגע נשאיר כדי שיתפוס את הכל אם יש חפיפה.

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
def consult_ai_agent(query: AIQueryRequest, db: Session = Depends(get_db)):
    events = db.query(Event).filter(Event.event_type == "TransactionCreated").all()
    transactions = [event.payload for event in events]
    
    try:
        ai_result = get_financial_advice(query.question, transactions)
        return AIQueryResponse(
            answer=ai_result.get("answer", ""),
            suggested_action=ai_result.get("suggested_action", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# --- Budget & Savings Endpoints ---

@app.get("/api/budget", response_model=BudgetDataResponse)
def get_budget_data(db: Session = Depends(get_db)):
    budgets = db.query(BudgetCategory).all()
    subs = db.query(Subscription).all()
    savings = db.query(SavingsGoal).all()
    return {
        "budgets": [{"name": b.name, "limit": b.limit_amount, "spent": b.spent_amount} for b in budgets],
        "subscriptions": [{"name": s.name, "amount": s.amount} for s in subs],
        "savings": [{"name": s.name, "target": s.target_amount, "current": s.current_amount} for s in savings]
    }

@app.post("/api/budget/savings")
def add_savings_goal(goal: SavingsGoalCreate, db: Session = Depends(get_db)):
    new_goal = SavingsGoal(name=goal.name, target_amount=goal.target, current_amount=goal.current)
    db.add(new_goal)
    db.commit()
    return {"status": "success", "id": new_goal.id}

@app.post("/api/budget/category")
def add_budget_category(item: BudgetCategoryCreate, db: Session = Depends(get_db)):
    
    # 1. שליפת כל העסקאות
    events = db.query(Event).filter(Event.event_type == "TransactionCreated").all()
    past_spent = 0.0
    budget_name = item.name.strip()
    
    # 2. מעבר על העסקאות וחיפוש התאמה דו-כיוונית
    for event in events:
        data = event.payload
        trans_cat = data.get("category", "").strip()
        trans_amount = float(data.get("amount_in_ils", 0.0))
        
        # התאמה: אם שם הקטגוריה נמצא בשם התקציב או להיפך
        if trans_cat and (trans_cat in budget_name or budget_name in trans_cat):
             past_spent += trans_amount

    # 3. יצירת התקציב עם הסכום שחושב
    new_cat = BudgetCategory(name=item.name, limit_amount=item.limit_amount, spent_amount=past_spent)
    db.add(new_cat)
    db.commit()
    return {"status": "success", "id": new_cat.id}

@app.post("/api/budget/subscription")
def add_subscription(item: SubscriptionCreate, db: Session = Depends(get_db)):
    new_sub = Subscription(name=item.name, amount=item.amount)
    db.add(new_sub)
    db.commit()
    return {"status": "success", "id": new_sub.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)