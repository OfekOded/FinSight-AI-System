from PySide6.QtCore import QThread, Signal
from .agent_model import AgentModel

class AIWorker(QThread):
    finished = Signal(dict)

    def __init__(self, api_service, question, history):
        super().__init__()
        self.api_service = api_service
        self.question = question
        self.history = history

    def run(self):
        response = self.api_service.consult_ai(self.question, self.history)
        if response:
            self.finished.emit(response)
        else:
            self.finished.emit({"answer": "שגיאה בתקשורת עם השרת.", "suggested_action": ""})

class AgentPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        self.model = AgentModel()
        
        self.view.send_btn.clicked.connect(self.handle_send)
        self.view.user_input.returnPressed.connect(self.view.send_btn.click)

        self.greet_user()

    def greet_user(self):
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

        greeting_text = f"שלום {user_name}! אני היועץ הפיננסי שלך.\nאני מחובר לנתונים שלך ויכול לעזור לך לנתח הוצאות, לבנות תקציב או סתם לענות על שאלות.\n\nאיך אפשר לעזור היום?"
        self.view.add_message(greeting_text, is_user=False)

    def handle_send(self):
        question = self.view.user_input.text().strip()
        if not question:
            return

        self.view.add_message(question, is_user=True)
        self.view.clear_input()
        self.view.set_loading(True)
        
        self.worker = AIWorker(self.api_service, question, self.model.history)
        self.worker.finished.connect(self.handle_ai_response)
        self.worker.start()
        
        self.model.history.append({"role": "user", "content": question})

    def handle_ai_response(self, response):
        self.view.set_loading(False)
        
        answer = response.get("answer", "מצטער, לא הצלחתי להבין.")
        action = response.get("suggested_action", "")
        
        full_response = answer
        if action:
            full_response += f"\n\n💡 המלצה לפעולה: {action}"
            
        self.view.add_message(full_response, is_user=False)
        self.model.history.append({"role": "assistant", "content": answer})