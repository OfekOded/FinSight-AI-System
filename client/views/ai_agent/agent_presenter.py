from PySide6.QtCore import QThread, Signal

# שימוש ב-Thread כדי שהממשק לא יתקע בזמן שה-AI חושב
class AIWorker(QThread):
    finished = Signal(dict) # מחזיר מילון תשובה

    def __init__(self, api_service, question):
        super().__init__()
        self.api_service = api_service
        self.question = question

    def run(self):
        # הרצת השאילתה מול השרת בנפרד מהממשק
        response = self.api_service.consult_ai(self.question)
        if response:
            self.finished.emit(response)
        else:
            self.finished.emit({"answer": "שגיאה בתקשורת עם השרת.", "suggested_action": ""})

class AgentPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        
        # חיבור כפתור השליחה
        self.view.send_btn.clicked.connect(self.handle_send)
        
        # חיבור מקש Enter בשדה הטקסט
        self.view.user_input.returnPressed.connect(self.view.send_btn.click)

        # --- שליפת שם המשתמש לברכה דינמית ---
        self.greet_user()

    def greet_user(self):
        """פונקציה שמביאה את השם מהשרת ומציגה הודעת פתיחה אישית"""
        try:
            profile = self.api_service.get_user_profile()
            if profile and "full_name" in profile:
                user_name = profile["full_name"]
            elif profile and "username" in profile:
                user_name = profile["username"]
            else:
                user_name = "משתמש יקר"
        except:
            user_name = "משתמש יקר"

        # הודעת פתיחה דינמית
        greeting_text = (
            f"שלום {user_name}! אני היועץ הפיננסי שלך.\n"
            "אני מחובר לנתונים שלך ויכול לעזור לך לנתח הוצאות, לבנות תקציב או סתם לענות על שאלות.\n\n"
            "איך אפשר לעזור היום?"
        )
        
        self.view.add_message(greeting_text, is_user=False)

    def handle_send(self):
        question = self.view.user_input.text().strip()
        if not question:
            return

        # 1. הוספת הודעת המשתמש למסך
        self.view.add_message(question, is_user=True)
        self.view.clear_input()
        
        # 2. כניסה למצב טעינה
        self.view.set_loading(True)
        
        # 3. הפעלת ה-AI ברקע (כדי לא לתקוע את התוכנה)
        self.worker = AIWorker(self.api_service, question)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.start()

    def handle_ai_response(self, response):
        self.view.set_loading(False)
        
        answer = response.get("answer", "מצטער, לא הצלחתי להבין.")
        action = response.get("suggested_action", "")
        
        # הוספת התשובה של ה-AI
        full_response = answer
        if action:
            full_response += f"\n\n💡 המלצה לפעולה: {action}"
            
        self.view.add_message(full_response, is_user=False)