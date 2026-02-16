from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QLineEdit, QDoubleSpinBox, QMessageBox, QGraphicsDropShadowEffect, QFormLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class ModernCard(QFrame):
    def __init__(self, title, value, icon_emoji="👤"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #dfe6e9;
            }
        """)
        # אפקט צל
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        
        # כותרת ואייקון
        top_row = QHBoxLayout()
        lbl_icon = QLabel(icon_emoji)
        lbl_icon.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #636e72; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        
        top_row.addWidget(lbl_icon)
        top_row.addWidget(lbl_title)
        top_row.addStretch()
        
        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet("color: #2d3436; font-size: 22px; font-weight: bold; margin-top: 5px; border: none; background: transparent;")
        
        layout.addLayout(top_row)
        layout.addWidget(self.lbl_value)

class ProfileView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f6fa;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # כותרת ראשית
        header = QLabel("האזור האישי שלי")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d3436; margin-bottom: 10px;")
        main_layout.addWidget(header)

        # רשת כרטיסים (תצוגה נוכחית)
        cards_layout = QHBoxLayout()
        
        self.card_name = ModernCard("שם משתמש", "אורח", "👋")
        self.card_salary = ModernCard("משכורת מעודכנת", "₪0", "💰")
        self.card_role = ModernCard("סטטוס", "מחובר", "⭐")
        
        cards_layout.addWidget(self.card_name)
        cards_layout.addWidget(self.card_salary)
        cards_layout.addWidget(self.card_role)
        
        main_layout.addLayout(cards_layout)
        
        # אזור עריכה (הטופס שהיה חסר!)
        edit_frame = QFrame()
        edit_frame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 15px; padding: 20px; }
            QLabel { color: #333; font-weight: bold; font-size: 14px; }
            QLineEdit, QDoubleSpinBox { 
                padding: 10px; border: 1px solid #dfe6e9; border-radius: 8px; font-size: 14px; background-color: #fdfdfd;
            }
            QLineEdit:focus, QDoubleSpinBox:focus { border: 1px solid #0984e3; }
        """)
        
        edit_layout = QVBoxLayout(edit_frame)
        
        lbl_edit = QLabel("עדכון פרטים אישיים")
        lbl_edit.setStyleSheet("font-size: 18px; margin-bottom: 15px; color: #2d3436;")
        edit_layout.addWidget(lbl_edit)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # שדה שם מלא
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("הכנס שם מלא חדש")
        form_layout.addRow("שם מלא:", self.name_input)

        # שדה משכורת (מספרי)
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setRange(0, 1000000)
        self.salary_input.setPrefix("₪ ")
        self.salary_input.setButtonSymbols(QDoubleSpinBox.NoButtons) # ללא חצים קטנים
        form_layout.addRow("משכורת חודשית:", self.salary_input)

        # שדה סיסמה
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("השאר ריק כדי לשמור על הסיסמה הנוכחית")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("סיסמה חדשה:", self.password_input)

        edit_layout.addLayout(form_layout)

        # כפתור שמירה
        self.save_btn = QPushButton("שמור שינויים")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #00b894; 
                color: white; 
                border-radius: 8px; 
                padding: 12px; 
                font-weight: bold; 
                font-size: 15px; 
                margin-top: 15px;
            }
            QPushButton:hover { background-color: #00a884; }
            QPushButton:pressed { background-color: #008f72; }
        """)
        edit_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(edit_frame)
        main_layout.addStretch()

    def update_display(self, name, salary):
        """פונקציה לעדכון הכרטיסים למעלה"""
        self.card_name.lbl_value.setText(name)
        self.card_salary.lbl_value.setText(f"₪{salary:,.0f}")

    def show_message(self, title, message, is_error=False):
        if is_error:
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)