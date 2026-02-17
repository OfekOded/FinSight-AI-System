from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLineEdit, QScrollArea, QLabel, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette

class ChatBubble(QFrame):
    def __init__(self, text, is_user=False):
        super().__init__()
        self.setFrameShape(QFrame.NoFrame)
        self.setLineWidth(0)
        
        # הגדרת פריסה פנימית לבועה
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12) 
        
        # לייבל הטקסט
        self.lbl_text = QLabel(text)
        self.lbl_text.setWordWrap(True) # גלישת שורות אוטומטית
        self.lbl_text.setTextInteractionFlags(Qt.TextSelectableByMouse) # אפשרות להעתיק טקסט
        self.lbl_text.setStyleSheet("border: none; background-color: transparent;")
        
        # עיצוב לפי סוג השולח
        if is_user:
            # עיצוב בועה של המשתמש (כחול, טקסט לבן, צד שמאל)
            color = "#0984e3"
            text_color = "white"
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 18px;
                    border-bottom-right-radius: 0px; /* הפינה ה"דוקרת" */
                }}
                QLabel {{ color: {text_color}; font-size: 16px; font-weight: 500; }}
            """)
        else:
            # עיצוב בועה של ה-AI (אפור בהיר, טקסט כהה, צד ימין)
            color = "#dfe6e9" 
            text_color = "#2d3436"
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 18px;
                    border-bottom-left-radius: 0px; /* הפינה ה"דוקרת" */
                }}
                QLabel {{ color: {text_color}; font-size: 16px; font-weight: 500; }}
            """)

        layout.addWidget(self.lbl_text)
        
        # הגבלת רוחב הבועה שלא תתפוס את כל המסך
        self.setMaximumWidth(700) 
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

class AgentView(QWidget):
    def __init__(self):
        super().__init__()
        
        # פריסה ראשית של המסך
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- כותרת עליונה ---
        header = QFrame()
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #dfe6e9;")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("FinSight AI Advisor")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d3436; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.main_layout.addWidget(header)

        # --- אזור הצ'אט (גלילה) ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: #f1f2f6; }
            QScrollBar:vertical { width: 10px; background: transparent; }
            QScrollBar::handle:vertical { background: #b2bec3; border-radius: 5px; }
        """)
        
        # הקונטיינר שמחזיק את כל הבועות
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background-color: #f1f2f6;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(10) # רווח בין הודעות
        self.chat_layout.addStretch() # דוחף את ההודעות למטה בהתחלה
        
        self.scroll_area.setWidget(self.chat_container)
        self.main_layout.addWidget(self.scroll_area)

        # --- אזור ההקלדה (למטה) ---
        input_container = QFrame()
        input_container.setStyleSheet("background-color: white; border-top: 1px solid #dfe6e9;")
        input_container.setFixedHeight(80)
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(20, 10, 20, 10)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("שאל אותי כל שאלה פיננסית...")
        self.user_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dfe6e9; border-radius: 20px; padding: 10px 15px; font-size: 14px; background-color: #fdfdfd;
            }
            QLineEdit:focus { border: 1px solid #0984e3; }
        """)
        
        self.send_btn = QPushButton("שלח")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0984e3; color: white; border-radius: 20px; 
                padding: 10px 20px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #007bb5; }
            QPushButton:disabled { background-color: #b2bec3; }
        """)
        
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_btn)
        
        self.main_layout.addWidget(input_container)

    def add_message(self, text, is_user):
        """פונקציה להוספת בועה חדשה לצ'אט"""
        bubble = ChatBubble(text, is_user)
        
        # יצירת שורה חדשה כדי לשלוט ביישור (ימין/שמאל)
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_user:
            # משתמש: הצמדה לשמאל (Stretch מימין)
            bubble_align = Qt.AlignLeft
            row_layout.addWidget(bubble)
            row_layout.addStretch()
        else:
            # AI: הצמדה לימין (Stretch משמאל)
            bubble_align = Qt.AlignRight
            row_layout.addStretch()
            row_layout.addWidget(bubble)
            
        self.chat_layout.addWidget(row_widget)
        
        # גלילה אוטומטית למטה
        # אנחנו משתמשים בטיימר קצרצר כדי לתת ל-GUI זמן להתעדכן לפני הגלילה
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_input(self):
        self.user_input.clear()

    def set_loading(self, is_loading):
        if is_loading:
            self.send_btn.setEnabled(False)
            self.send_btn.setText("...")
        else:
            self.send_btn.setEnabled(True)
            self.send_btn.setText("שלח")