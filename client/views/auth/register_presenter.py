# client/views/auth/register_presenter.py

class RegisterPresenter:
    def __init__(self, view, api_service, on_register_success, on_back_to_login):
        self.view = view
        self.api_service = api_service
        self.on_register_success = on_register_success
        self.on_back_to_login = on_back_to_login

        self.view.register_btn.clicked.connect(self.handle_register)
        self.view.back_to_login_btn.clicked.connect(self.on_back_to_login)

    def handle_register(self):
        full_name = self.view.fullname_input.text()
        username = self.view.username_input.text()
        password = self.view.password_input.text()
        confirm = self.view.confirm_pass_input.text()

        # בדיקות מקומיות (Client Side Validation)
        if not all([full_name, username, password, confirm]):
            self.view.show_message("שגיאה", "נא למלא את כל השדות", True)
            return

        if password != confirm:
            self.view.show_message("שגיאה", "הסיסמאות אינן תואמות", True)
            return

        # שליחה לשרת
        print(f"Registering user: {username}")
        result = self.api_service.register(username, password, full_name)

        if result:
            self.view.show_message("הצלחה", "ההרשמה בוצעה בהצלחה! כעת ניתן להתחבר.")
            # מעבר למסך ההתחברות
            self.on_register_success() 
        else:
            self.view.show_message("שגיאה", "ההרשמה נכשלה (ייתכן שהמשתמש כבר קיים)", True)