# transaction_view.py - מציג את טופס ההוספה, בוחר התאריך ואזור הגרירה (Drag & Drop) של הקבלות.
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QDateEdit, QPushButton, QMessageBox, QFormLayout)
from PySide6.QtCore import Qt, QDate

class TransactionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # כותרת
        self.title = QLabel("הוספת הוצאה חדשה")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # טופס
        self.form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("לדוגמה: קניות בסופר")
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        
        self.category_input = QComboBox()
        self.category_input.addItems(["מזון", "דלק", "בילויים", "קניות", "שכר דירה", "ארנונה", "אחר"])
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.form_layout.addRow("תיאור:", self.title_input)
        self.form_layout.addRow("סכום (₪):", self.amount_input)
        self.form_layout.addRow("קטגוריה:", self.category_input)
        self.form_layout.addRow("תאריך:", self.date_input)
        
        self.layout.addLayout(self.form_layout)

        # כפתור שמירה
        self.save_btn = QPushButton("שמור עסקה")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF; color: white; padding: 10px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
        self.layout.addWidget(self.save_btn)
        
        self.layout.addStretch() # דוחף את הכל למעלה

    def get_data(self):
        """פונקציה שהפרזנטר יקרא לה כדי לקבל את המידע מהשדות"""
        return {
            "title": self.title_input.text(),
            "amount": self.amount_input.text(),
            "category": self.category_input.currentText(),
            "date": self.date_input.date().toString("yyyy-MM-dd")
        }

    def show_message(self, title, message, is_error=False):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical if is_error else QMessageBox.Information)
        msg.exec()
        
    def clear_form(self):
        self.title_input.clear()
        self.amount_input.clear()
        self.date_input.setDate(QDate.currentDate())