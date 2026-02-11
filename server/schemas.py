from pydantic import BaseModel
from typing import List, Optional

# --- Transaction Models ---

class TransactionCreate(BaseModel):
    """
    Schema for creating a new transaction.
    Received from the Client.
    """
    title: str
    amount: float
    currency: str = "ILS"  # Default currency is Shekels
    category: str
    date: str  # Expected format: YYYY-MM-DD
    image_url: Optional[str] = None

class TransactionResponse(TransactionCreate):
    """
    Schema for returning a transaction to the Client.
    Includes the system-generated ID and status.
    """
    id: str
    amount_in_ils: float # Calculated field based on exchange rate
    status: str

# --- Dashboard Models ---

class DashboardData(BaseModel):
    """
    Aggregated data for the main dashboard view.
    """
    total_balance: float
    monthly_expenses: float
    recent_transactions: List[TransactionResponse]

# --- AI Models ---

class AIQueryRequest(BaseModel):
    question: str

class AIQueryResponse(BaseModel):
    answer: str
    suggested_action: Optional[str] = None
    
    
    
    
# --- Auth Models ---

class UserRegister(BaseModel):
    """
    Schema for user registration
    """
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    """
    Schema for user login
    """
    username: str
    password: str

class AuthResponse(BaseModel):
    """
    Response returned after successful login/register
    """
    token: str
    username: str
    status: str = "success"





# --- Budget Models ---

class BudgetSchema(BaseModel):
    name: str
    limit: float
    spent: float

class SubscriptionSchema(BaseModel):
    name: str
    amount: float

class SavingsGoalSchema(BaseModel):
    name: str
    target: float
    current: float

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