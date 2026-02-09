import uuid
import requests
import hashlib
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from schemas import (
    TransactionCreate,
    TransactionResponse,
    DashboardData,
    AIQueryRequest,
    AIQueryResponse,
    UserRegister,
    UserLogin,
    AuthResponse
)
from database import engine, Base, get_db
from models import Event, User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinSight AI Backend System")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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



# --- AUTHENTICATION ---
@app.post("/api/auth/register", response_model=AuthResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    print(f"[Server] Registering new user: {user.username}")
    
    # 1. בדיקה אם המשתמש כבר קיים
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 2. יצירת משתמש חדש עם סיסמה מוצפנת
    new_user = User(
        username=user.username,
        full_name=user.full_name,
        password_hash=hash_password(user.password) # מצפינים!
    )
    
    # 3. שמירה ב-DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "token": f"token-{new_user.id}", # בייצור אמיתי משתמשים ב-JWT
        "username": new_user.username,
        "status": "created"
    }

@app.post("/api/auth/login", response_model=AuthResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    print(f"[Server] Login attempt for: {user.username}")
    
    # 1. שליפת המשתמש מה-DB
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user:
        # אם המשתמש לא קיים
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # 2. בדיקה אם הסיסמה שהוזנה (אחרי הצפנה) תואמת למה ששמור ב-DB
    if db_user.password_hash != hash_password(user.password):
        # סיסמה שגויה
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # 3. התחברות מוצלחת
    return {
        "token": f"token-{db_user.id}",
        "username": db_user.username,
        "status": "logged_in"
    }
    
    
    
    
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