# main_window_model.py - מחזיק את המצב (State) של החלון הראשי, למשל: איזה עמוד מוצג כרגע ומי המשתמש המחובר.
from dataclasses import dataclass

@dataclass
class MainWindowModel:
    current_view_index: int = 0
    username: str = "משתמש אורח" # הכנה לעתיד, כרגע אין מערכת התחברות אבל זה יכול להיות שימושי בהמשך.