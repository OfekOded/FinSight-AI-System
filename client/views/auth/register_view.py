# client/views/auth/register_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt

class RegisterView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinSight - הרשמה")
        self.resize(400, 550)
        self.setStyleSheet("background-color: #f5f6fa;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # כרטיס הרשמה
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #dcdde1;
            }
        """)
        self.card.setFixedSize(350, 450)
        card_layout = QVBoxLayout(self.card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(30, 30, 30, 30)

        # כותרת
        title = QLabel("יצירת חשבון חדש 🚀")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2f3640; margin-bottom: 10px;")
        
        # שדות קלט
        self.fullname_input = self.create_input("שם מלא")
        self.username_input = self.create_input("שם משתמש (באנגלית)")
        self.password_input = self.create_input("סיסמה", is_password=True)
        self.confirm_pass_input = self.create_input("אימות סיסמה", is_password=True)

        # כפתור הרשמה
        self.register_btn = QPushButton("הירשם")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)

        # כפתור חזרה להתחברות
        self.back_to_login_btn = QPushButton("כבר רשום? התחבר כאן")
        self.back_to_login_btn.setCursor(Qt.PointingHandCursor)
        self.back_to_login_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7f8c8d;
                border: none;
            }
            QPushButton:hover { color: #2ecc71; text-decoration: underline; }
        """)

        card_layout.addWidget(title)
        card_layout.addWidget(self.fullname_input)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.confirm_pass_input)
        card_layout.addWidget(self.register_btn)
        card_layout.addWidget(self.back_to_login_btn)
        card_layout.addStretch()

        layout.addWidget(self.card)
        
        self.username_input.returnPressed.connect(self.register_btn.click)
        self.password_input.returnPressed.connect(self.register_btn.click)
        self.fullname_input.returnPressed.connect(self.register_btn.click)

    def create_input(self, placeholder, is_password=False):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        if is_password:
            inp.setEchoMode(QLineEdit.Password)
        inp.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdde1; border-radius: 8px; padding: 10px; background-color: #f1f2f6;
            }
            QLineEdit:focus { border: 1px solid #2ecc71; background-color: white; }
        """)
        return inp

    def show_message(self, title, msg, is_error=False):
        icon = QMessageBox.Critical if is_error else QMessageBox.Information
        QMessageBox(icon, title, msg, QMessageBox.Ok, self).exec()