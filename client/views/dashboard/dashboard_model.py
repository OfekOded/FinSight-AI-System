# dashboard_model.py - מבנה הנתונים (Data Class) של הדשבורד: מחזיק את היתרה, ההוצאות והרשימה לעיבוד.
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class DashboardModel:
    total_balance: float = 0.0
    monthly_expenses: float = 0.0
    recent_transactions: List[Dict] = field(default_factory=list)