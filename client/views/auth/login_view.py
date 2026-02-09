from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinSight - התחברות")
        self.resize(400, 500)
        self.setStyleSheet("background-color: #f5f6fa;")

        # לייאוט ראשי
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # --- כרטיס התחברות (Frame לבן במרכז) ---
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #dcdde1;
            }
        """)
        self.card.setFixedSize(350, 400)
        card_layout = QVBoxLayout(self.card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(30, 30, 30, 30)

        # כותרת
        title = QLabel("ברוכים הבאים 👋")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2f3640; margin-bottom: 10px;")
        
        # שדות קלט
        self.username_input = self.create_input("שם משתמש")
        self.password_input = self.create_input("סיסמה", is_password=True)

        # כפתור התחברות
        self.login_btn = QPushButton("התחבר למערכת")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d2d3;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 12px;
                border-radius: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #01a3a4;
            }
        """)

        # כפתור מעבר להרשמה (Link)
        self.register_link = QPushButton("אין לך חשבון? הרשם כאן")
        self.register_link.setCursor(Qt.PointingHandCursor)
        self.register_link.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #576574;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                color: #00d2d3;
                text-decoration: underline;
            }
        """)

        # הוספה לכרטיס
        card_layout.addWidget(title)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.login_btn)
        card_layout.addWidget(self.register_link)
        card_layout.addStretch()

        # הוספת הכרטיס למסך הראשי
        layout.addWidget(self.card)

    def create_input(self, placeholder, is_password=False):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        if is_password:
            inp.setEchoMode(QLineEdit.Password)
        
        inp.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f1f2f6;
            }
            QLineEdit:focus {
                border: 1px solid #00d2d3;
                background-color: white;
            }
        """)
        return inp

    def show_error(self, message):
        QMessageBox.warning(self, "שגיאת התחברות", message)