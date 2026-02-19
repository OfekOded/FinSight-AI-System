from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                               QDoubleSpinBox, QHBoxLayout, QMessageBox, QWidget, QAbstractSpinBox)
from PySide6.QtCore import Qt

class SavingsActionDialog(QDialog):
    def __init__(self, parent, name, current, target):
        super().__init__(parent)
        self.setWindowTitle(f"ניהול חיסכון: {name}")
        self.setFixedWidth(350)
        self.setStyleSheet("background-color: white;")
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.amount_to_add = 0
        self.action = None 
        self.is_completed = current >= target

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # כותרת
        title_lbl = QLabel(f"כמה להוסיף ל-{name}?")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d3436;")
        layout.addWidget(title_lbl)
        
        status_lbl = QLabel(f"מצב נוכחי: {current:,.0f} / {target:,.0f} ₪")
        status_lbl.setStyleSheet("color: #636e72;")
        layout.addWidget(status_lbl)
        
        # שדה קלט להוספה - עיצוב נקי ללא כפתורים
        self.input_amount = QDoubleSpinBox()
        self.input_amount.setRange(0, 1000000)
        self.input_amount.setSuffix(" ₪")
        self.input_amount.setButtonSymbols(QAbstractSpinBox.NoButtons) # התיקון: מעלים את החצים
        self.input_amount.setStyleSheet("""
            QDoubleSpinBox { 
                padding: 10px; 
                border: 2px solid #dfe6e9; 
                border-radius: 8px; 
                font-size: 16px; 
                background-color: #fdfdfd;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #0984e3;
            }
        """)
        layout.addWidget(self.input_amount)
        
        # כפתור הוספה
        self.btn_add = QPushButton("שמור והוסף")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton { background-color: #0984e3; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #74b9ff; }
        """)
        self.btn_add.clicked.connect(self.on_deposit)
        layout.addWidget(self.btn_add)
        
        layout.addSpacing(10)
        
        # --- אזור פעולות מתקדמות ---
        advanced_frame = QWidget()
        adv_layout = QVBoxLayout(advanced_frame)
        adv_layout.setContentsMargins(0,0,0,0)
        
        if self.is_completed:
            self.btn_finish = QPushButton("סיום יעד)")
            self.btn_finish.setCursor(Qt.PointingHandCursor)
            self.btn_finish.setStyleSheet("""
                QPushButton { background-color: #00b894; color: white; padding: 10px; border-radius: 5px; font-weight: bold; }
                QPushButton:hover { background-color: #55efc4; }
            """)
            self.btn_finish.clicked.connect(self.on_finish)
            adv_layout.addWidget(self.btn_finish)
            
            info = QLabel("לחיצה תסיר את היעד מהרשימה, אך הכסף ייחשב כהוצאה שבוצעה.")
            info.setWordWrap(True)
            info.setStyleSheet("font-size: 11px; color: #636e72;")
            adv_layout.addWidget(info)
            adv_layout.addSpacing(5)

        self.btn_cancel = QPushButton("בטל ומחק יעד")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton { background-color: white; color: #d63031; border: 1px solid #d63031; padding: 8px; border-radius: 5px; }
            QPushButton:hover { background-color: #fab1a0; }
        """)
        self.btn_cancel.clicked.connect(self.on_cancel)
        adv_layout.addWidget(self.btn_cancel)
        
        layout.addWidget(advanced_frame)

    def on_deposit(self):
        val = self.input_amount.value()
        if val <= 0: return
        self.amount_to_add = val
        self.action = 'deposit'
        self.accept()

    def on_finish(self):
        reply = QMessageBox.question(self, "סיום יעד", "מזל טוב! האם אתה בטוח שברצונך לסיים את היעד ולהסיר אותו מהרשימה?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.action = 'finish'
            self.accept()

    def on_cancel(self):
        reply = QMessageBox.question(self, "ביטול יעד", "האם אתה בטוח? היעד יימחק והכסף יחזור ליתרה.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.action = 'cancel'
            self.accept()