# client/views/transactions/transaction_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QDateEdit, QFrame, QMessageBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont, QColor

class TransactionView(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # --- עיצוב כללי ---
        self.setStyleSheet("background-color: transparent;")

        # לייאוט ראשי שממרכז את הכרטיס
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.card = QFrame()
        self.card.setFixedWidth(650)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 20px;
                border: 1px solid #f0f0f0;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.card.setGraphicsEffect(shadow)

        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(25)
        self.card_layout.setContentsMargins(45, 45, 45, 45)

        self.title = QLabel("הוספת הוצאה חדשה")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 26px; 
            font-weight: bold; 
            color: #2c3e50;
            border: none;
        """)
        self.card_layout.addWidget(self.title)

        self.form_layout = QGridLayout()
        self.form_layout.setVerticalSpacing(20)
        self.form_layout.setHorizontalSpacing(25)

        input_style = """
            QLineEdit, QComboBox, QDateEdit {
                background-color: #f7f9fc;
                border: 1px solid #e1e5eb;
                border-radius: 12px;
                padding: 12px;
                font-family: 'Segoe UI';
                font-size: 15px;
                color: #2d3436;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #00d2d3; 
                background-color: #ffffff;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #2d3436;
                selection-background-color: #00d2d3;
                selection-color: white;
            }
        """


        calendar_style = """
            QCalendarWidget QWidget {
                background-color: white; 
                alternate-background-color: #f7f9fc;
                color: black;
            }
            QCalendarWidget QToolButton {
                color: black;
                background-color: transparent;
                icon-size: 20px;
                border: none;
                font-weight: bold;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: black;  /* צבע המספרים */
                background-color: white;
                selection-background-color: #00d2d3; /* צבע הבחירה (טורקיז) */
                selection-color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                color: black;
            }
        """
        
        label_style = """
            QLabel {
                font-family: 'Segoe UI';
                font-size: 14px; 
                font-weight: 600; 
                color: #636e72;
                border: none;
            }
        """

        lbl_date = QLabel("תאריך:")
        lbl_date.setStyleSheet(label_style)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet(input_style + calendar_style)
        self.date_input.setFixedHeight(48)

        lbl_cat = QLabel("קטגוריה:")
        lbl_cat.setStyleSheet(label_style)
        self.category_input = QComboBox()
        self.category_input.addItems(["מזון", "דלק", "בילויים", "קניות", "שכר דירה", "ארנונה", "אחר"])
        self.category_input.setStyleSheet(input_style)
        self.category_input.setFixedHeight(48)

        self.form_layout.addWidget(lbl_date, 0, 0)
        self.form_layout.addWidget(self.date_input, 1, 0)
        self.form_layout.addWidget(lbl_cat, 0, 1)
        self.form_layout.addWidget(self.category_input, 1, 1)

        lbl_amount = QLabel("סכום (₪):")
        lbl_amount.setStyleSheet(label_style)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setStyleSheet(input_style)
        self.amount_input.setFixedHeight(48)

        lbl_curr = QLabel("מטבע:")
        lbl_curr.setStyleSheet(label_style)
        self.currency_input = QComboBox()
        self.currency_input.addItems(["ILS", "USD", "EUR"])
        self.currency_input.setStyleSheet(input_style)
        self.currency_input.setFixedHeight(48)

        self.form_layout.addWidget(lbl_amount, 2, 0)
        self.form_layout.addWidget(self.amount_input, 3, 0)
        self.form_layout.addWidget(lbl_curr, 2, 1)
        self.form_layout.addWidget(self.currency_input, 3, 1)

        lbl_desc = QLabel("תיאור:")
        lbl_desc.setStyleSheet(label_style)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("לדוגמה: קניות בסופר")
        self.title_input.setStyleSheet(input_style)
        self.title_input.setFixedHeight(48)

        self.form_layout.addWidget(lbl_desc, 4, 0, 1, 2)
        self.form_layout.addWidget(self.title_input, 5, 0, 1, 2)

        self.card_layout.addLayout(self.form_layout)
        self.card_layout.addSpacing(20)

        # --- כפתור שמירה ---
        self.save_btn = QPushButton("שמור עסקה")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFixedHeight(55)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d2d3; 
                color: white;
                font-family: 'Segoe UI';
                font-size: 18px; 
                font-weight: bold;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #00cec9;
                margin-top: -2px;
            }
            QPushButton:pressed {
                background-color: #01a3a4;
                margin-top: 0px;
            }
        """)
        self.card_layout.addWidget(self.save_btn)

        self.layout.addWidget(self.card)


    def get_data(self):
        """פונקציה שהפרזנטר יקרא לה כדי לקבל את המידע מהשדות"""
        return {
            "title": self.title_input.text(),
            "amount": self.amount_input.text(),
            "category": self.category_input.currentText(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "currency": self.currency_input.currentText()   #תוספת של סוג המטבע צריך להוסיף בקוד כדי שיהיה לנו שימוש ב API 
        }

    def show_message(self, title, message, is_error=False):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical if is_error else QMessageBox.Information)
        msg.setStyleSheet("background-color: white; color: black;") 
        msg.exec()
        
    def clear_form(self):
        self.title_input.clear()
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())
        # איפוס פוקוס
        self.title_input.setFocus()