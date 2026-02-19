from sqlalchemy.orm import Session
from models import BudgetCategory

def project_transaction_created(payload: dict, db: Session):
    user_id = payload.get("user_id")
    category = payload.get("category", "").strip()
    amount = payload.get("amount_in_ils", 0.0)

    if not user_id or not category:
        return

    budgets = db.query(BudgetCategory).filter(BudgetCategory.user_id == user_id).all()
    
    for cat in budgets:
        budget_name = cat.name.strip()
        if category == budget_name:
            cat.spent_amount += amount

def dispatch_event(event_type: str, payload: dict, db: Session):
    if event_type == "TransactionCreated":
        project_transaction_created(payload, db)