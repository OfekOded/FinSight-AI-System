from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class TransactionCreate(BaseModel):
    title: str
    amount: float
    currency: str = "ILS"
    category: str
    date: str
    image_url: Optional[str] = None

class TransactionResponse(TransactionCreate):
    id: str
    amount_in_ils: float
    status: str

class DashboardData(BaseModel):
    total_balance: float
    monthly_expenses: float
    recent_transactions: List[TransactionResponse]

class Message(BaseModel):
    role: str
    content: str

class AIQueryRequest(BaseModel):
    question: str
    history: List[Message] = []

class AIQueryResponse(BaseModel):
    response: str
    suggested_action: Optional[str] = None

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    token: str
    username: str
    status: str = "success"

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    salary: Optional[float] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class BudgetSchema(BaseModel):
    id: int
    name: str
    limit_amount: float
    spent_amount: float
    model_config = ConfigDict(from_attributes=True)

class SubscriptionSchema(BaseModel):
    id: int
    name: str
    amount: float
    model_config = ConfigDict(from_attributes=True)

class SavingsGoalSchema(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    model_config = ConfigDict(from_attributes=True)

class SavingsGoalCreate(BaseModel):
    name: str
    target: float
    current: float = 0

class BudgetDataResponse(BaseModel):
    budgets: List[BudgetSchema]
    subscriptions: List[SubscriptionSchema]
    savings: List[SavingsGoalSchema]

class BudgetCategoryCreate(BaseModel):
    name: str
    limit_amount: float

class SubscriptionCreate(BaseModel):
    name: str
    amount: float