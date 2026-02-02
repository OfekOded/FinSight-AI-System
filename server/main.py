import uuid
import requests 
from fastapi import FastAPI, HTTPException
from typing import List

# Import our schemas
from schemas import (
    TransactionCreate, 
    TransactionResponse, 
    DashboardData, 
    AIQueryRequest, 
    AIQueryResponse
)

app = FastAPI(title="FinSight AI Backend System")

# --- Mock Database ---
mock_transactions = []

# --- Helper Function: External API Call ---
def get_exchange_rate(from_currency: str, to_currency: str = "ILS") -> float:
    """
    Fetches the current exchange rate from an external API.
    NOTE: In a real scenario, we would cache this result to avoid too many requests.
    """
    if from_currency == "ILS":
        return 1.0
    
    try:
        # Utilizing a public free API for exchange rates
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url)
        data = response.json()
        return data["rates"].get(to_currency, 1.0)
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return 1.0 # Fallback to 1.0 if API fails

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "FinSight System is online", "version": "1.0.0"}

@app.post("/api/transactions", response_model=TransactionResponse)
def add_transaction(transaction: TransactionCreate):
    """
    Receives a new transaction command.
    1. Fetches external exchange rate.
    2. Calculates amount in ILS.
    3. Saves to (Mock) DB.
    """
    
    # 1. External API Call requirement
    rate = get_exchange_rate(transaction.currency)
    final_amount_ils = transaction.amount * rate

    # 2. Simulate saving to DB
    new_id = str(uuid.uuid4())
    
    response_obj = {
        "id": new_id,
        "status": "confirmed",
        "amount_in_ils": final_amount_ils,
        **transaction.dict()
    }
    
    # Save to our temporary memory list
    mock_transactions.append(response_obj)
    
    return response_obj

@app.get("/api/dashboard", response_model=DashboardData)
def get_dashboard_data():
    """
    Returns aggregated data for the client dashboard.
    """
    # Simple calculation logic (Mock)
    total_spent = sum(t["amount_in_ils"] for t in mock_transactions)
    
    return {
        "total_balance": 20000.0 - total_spent, # Example starting balance
        "monthly_expenses": total_spent,
        "recent_transactions": mock_transactions[-5:] # Return last 5
    }

@app.post("/api/ai/consult", response_model=AIQueryResponse)
def consult_ai_agent(query: AIQueryRequest):
    """
    Sends a prompt to the AI Agent (Mock for now).
    """
    # Logic placeholder for LangChain integration
    return {
        "answer": f"Analysis based on your data: '{query.question}' is a valid concern. Spending trend is stable.",
        "suggested_action": "Review Subscription Costs"
    }

if __name__ == "__main__":
    import uvicorn
    # Run the server on localhost port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)