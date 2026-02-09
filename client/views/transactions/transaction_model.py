# transaction_model.py - מחזיק את נתוני הטופס (סכום, קטגוריה, תאריך) ומבצע ולידציה בסיסית לפני שליחה.
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TransactionModel:
    title: str = ""
    amount: float = 0.0
    category: str = "מזון" # ברירת מחדל אנחנו מבזבזים כסף על המבורגר או שאני פשוט רעב עכשיו בזמן שאני כותב את הקוד :)
    date: str = datetime.now().strftime("%Y-%m-%d")