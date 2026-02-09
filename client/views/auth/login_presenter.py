# client/views/auth/login_presenter.py

class LoginPresenter:
    def __init__(self, view, api_service, on_login_success, on_go_to_register):
        self.view = view
        self.api_service = api_service
        self.on_login_success = on_login_success
        self.on_go_to_register = on_go_to_register # פונקציה למעבר מסך

        self.view.login_btn.clicked.connect(self.handle_login)
        self.view.register_link.clicked.connect(self.on_go_to_register)

    def handle_login(self):
        username = self.view.username_input.text()
        password = self.view.password_input.text()

        if not username or not password:
            self.view.show_error("נא למלא שם משתמש וסיסמה")
            return

        # קריאה אמיתית לשרת
        user_data = self.api_service.login(username, password)

        if user_data:
            self.on_login_success(user_data)
        else:
            self.view.show_error("שם משתמש או סיסמה שגויים, או שגיאת שרת.")