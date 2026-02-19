from datetime import datetime
import uuid
import requests
import hashlib
from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
import shutil
import os
from sqlalchemy.orm import Session
from typing import List, Optional
from ai_agent import get_financial_advice, analyze_receipt_image
from projectors import dispatch_event

from schemas import (
    TransactionCreate,
    TransactionResponse,
    DashboardData,
    AIQueryRequest,
    AIQueryResponse,
    UserRegister,
    UserLogin,
    AuthResponse,
    UserProfileUpdate,
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

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        if "-" in authorization:
            user_id = authorization.split("-")[1]
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
        else:
            raise HTTPException(status_code=401, detail="Invalid token format")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
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

# --- Profile ---

@app.get("/api/auth/profile/me")
def get_my_profile(user: User = Depends(get_current_user)):
    return {"username": user.username, "full_name": user.full_name, "salary": user.salary}

@app.post("/api/user/profile")
def update_user_profile(update_data: UserProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if update_data.salary is not None:
        user.salary = update_data.salary
        
    if update_data.full_name:
        user.full_name = update_data.full_name

    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(status_code=400, detail="Current password required")
        
        if user.password_hash != hash_password(update_data.current_password):
            raise HTTPException(status_code=401, detail="Incorrect current password")
            
        user.password_hash = hash_password(update_data.new_password)

    db.commit()
    return {"status": "success", "salary": user.salary, "full_name": user.full_name}

# --- Receipts ---

@app.post("/api/receipts/analyze")
async def analyze_receipt(file: UploadFile = File(...)):
    """
    Receives an image file, sends it to Gemini Flash for OCR,
    and returns the extracted financial data.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read file into memory
        contents = await file.read()
        
        # Send to AI Agent
        result = await analyze_receipt_image(contents)
        
        return result
        
    except Exception as e:
        print(f"Error processing receipt: {e}")
        raise HTTPException(status_code=500, detail="Failed to process receipt image")
    
# --- BUSINESS LOGIC ---
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
        **transaction.dict()
    }

    new_event = Event(user_id=user.id, aggregate_id=new_id, event_type="TransactionCreated", payload=response_obj)
    db.add(new_event)
    
    dispatch_event("TransactionCreated", response_obj, db)
    
    db.commit()
    db.refresh(new_event)
    return response_obj


@app.get("/api/dashboard", response_model=DashboardData)
def get_dashboard_data(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    events = db.query(Event).filter(Event.user_id == user.id, Event.event_type == "TransactionCreated").all()
    transactions = []
    total_spent = 0.0
    
    for event in events:
        data = event.payload
        transactions.append(data)
        amount = data.get("amount_in_ils", data.get("amount", 0))
        total_spent += amount
            
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
    
    current_salary = user.salary if user.salary else 0.0
    balance = current_salary - total_monthly_spent

    return {
        "total_balance": balance,
        "monthly_expenses": total_spent,
        "recent_transactions": transactions[-5:]
    }
    

@app.post("/api/budget/category")
def add_budget_category(item: BudgetCategoryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    events = db.query(Event).filter(Event.user_id == user.id, Event.event_type == "TransactionCreated").all()
    past_spent = 0.0
    budget_name = item.name.strip()
    
    for event in events:
        data = event.payload
        trans_cat = data.get("category", "").strip()
        trans_amount = float(data.get("amount_in_ils", 0.0))
        
        if trans_cat == budget_name:
             past_spent += trans_amount

    new_cat = BudgetCategory(
        user_id=user.id,
        name=item.name, 
        limit_amount=item.limit_amount, 
        spent_amount=past_spent
    )
    db.add(new_cat)
    db.commit()
    return {"status": "success", "id": new_cat.id}

@app.post("/api/ai/consult", response_model=AIQueryResponse)
async def consult_ai_agent(query: AIQueryRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    events = db.query(Event).filter(Event.user_id == user.id, Event.event_type == "TransactionCreated").all()
    transactions = [event.payload for event in events]
    
    try:
        ai_result = await get_financial_advice(query.question, transactions)
        return AIQueryResponse(
            answer=ai_result.get("answer", ""),
            suggested_action=ai_result.get("suggested_action", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Budget & Savings Endpoints ---

@app.get("/api/budget", response_model=BudgetDataResponse)
def get_budget_data(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    budgets = db.query(BudgetCategory).filter(BudgetCategory.user_id == user.id).all()
    subs = db.query(Subscription).filter(Subscription.user_id == user.id).all()
    savings = db.query(SavingsGoal).filter(SavingsGoal.user_id == user.id).all()
    return {
        "budgets": budgets,
        "subscriptions": subs,
        "savings": savings
    }

# --- Savings Management Extensions ---

@app.put("/api/budget/savings/{goal_id}/deposit")
def deposit_to_savings(goal_id: int, amount: float = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    goal = db.query(SavingsGoal).filter(SavingsGoal.id == goal_id, SavingsGoal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
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
        raise HTTPException(status_code=404, detail="Goal not found")
    
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
    new_sub = Subscription(
        user_id=user.id, 
        name=item.name, 
        amount=item.amount
        )
    db.add(new_sub)
    db.commit()
    return {"status": "success", "id": new_sub.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)