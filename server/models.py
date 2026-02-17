from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey
from datetime import datetime
from database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    aggregate_id = Column(String, index=True)
    event_type = Column(String)
    payload = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # שם משתמש הוא מפתח
    full_name = Column(String)
    password_hash = Column(String) # אנחנו שומרים הצפנה של הסיסמה
    salary = Column(Float, default=10000.0)

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    limit_amount = Column(Float)
    spent_amount = Column(Float, default=0.0)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # מקשר למשתמש
    name = Column(String)
    amount = Column(Float)
    renewal_date = Column(Integer, default=1) # יום בחודש שבו מתחדש

class SavingsGoal(Base):
    __tablename__ = "savings_goals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)