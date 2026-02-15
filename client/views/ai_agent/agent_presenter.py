from PySide6.QtCore import QThread, Signal
from .agent_model import AgentModel

class AIWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, api_service, question):
        super().__init__()
        self.api_service = api_service
        self.question = question

    def run(self):
        try:
            res = self.api_service.consult_ai(self.question)
            if res:
                self.finished.emit(res)
            else:
                self.error.emit("Communication error")
        except Exception as e:
            self.error.emit(str(e))

class AgentPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        self.model = AgentModel()
        self.worker = None
        
        self.view.send_btn.clicked.connect(self.handle_send)

    def handle_send(self):
        question = self.view.get_question()
        if not question.strip():
            return
        
        self.view.append_message("אני", question)
        self.view.clear_input()
        self.view.send_btn.setEnabled(False)
        self.view.send_btn.setText("חושב...")
        
        self.worker = AIWorker(self.api_service, question)
        self.worker.finished.connect(self.on_result)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_result(self, response):
        self.view.send_btn.setEnabled(True)
        self.view.send_btn.setText("שלח")
        
        if "answer" in response:
            self.view.append_message("FinSight AI", response["answer"])
            if response.get("suggested_action"):
                self.view.append_message("הצעה לפעולה", response["suggested_action"])
        else:
            self.view.append_message("מערכת", "שגיאה בפורמט התשובה.")

    def on_error(self, err):
        self.view.send_btn.setEnabled(True)
        self.view.send_btn.setText("שלח")
        self.view.append_message("מערכת", "שגיאה בתקשורת עם השרת.")