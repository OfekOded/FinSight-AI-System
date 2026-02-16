# client/main.py
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from api_service import ApiService

# ייבוא כל המסכים
from views.auth.login_view import LoginView
from views.auth.login_presenter import LoginPresenter
from views.auth.register_view import RegisterView
from views.auth.register_presenter import RegisterPresenter
from views.main_window.main_window_view import MainWindowView
from views.main_window.main_window_presenter import MainWindowPresenter

class AppController:
    def __init__(self):
        self.api_service = ApiService()
        self.current_window = None # מחזיק את החלון הפעיל כרגע

    def start(self):
        self.show_login()

    def show_login(self):
        self.close_current_window()
        
        self.view = LoginView()
        # אנחנו מעבירים שתי פונקציות: אחת להצלחה, אחת למעבר להרשמה
        self.presenter = LoginPresenter(
            self.view, 
            self.api_service, 
            on_login_success=self.switch_to_dashboard,
            on_go_to_register=self.show_register
        )
        self.current_window = self.view
        self.view.show()

    def show_register(self):
        self.close_current_window()
        
        self.view = RegisterView()
        self.presenter = RegisterPresenter(
            self.view, 
            self.api_service, 
            on_register_success=self.show_login,
            on_back_to_login=self.show_login
        )
        self.view.switch_to_login_signal.connect(self.show_login_window)
        self.view.show()

    def switch_to_dashboard(self, user_data):
        self.close_current_window()
        print(f"Opening dashboard for {user_data.get('username')}")
        
        self.view = MainWindowView()
        # אפשר להעביר כאן את שם המשתמש למודל אם רוצים
        self.presenter = MainWindowPresenter(self.view, self.api_service)
        
        self.current_window = self.view
        self.view.show()

    def close_current_window(self):
        if self.current_window:
            self.current_window.close()
            self.current_window = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    
    app.setStyle("Fusion")
    app.setStyleSheet("QWidget { color: #2d3436; }") 

    controller = AppController()
    controller.start()
    
    sys.exit(app.exec())