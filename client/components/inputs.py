from PySide6.QtWidgets import QDateEdit, QLineEdit
from PySide6.QtCore import Qt

class ModernDateEdit(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDisplayFormat("dd/MM/yyyy")
        self.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border: 1px solid #dfe6e9;
                border-radius: 8px;
                font-size: 14px;
                background: #fdfdfd;
                min-height: 20px;
            }
            QDateEdit:focus {
                border: 1px solid #0984e3;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
        """)

class ModernInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QLineEdit { 
                padding: 12px; 
                border: 1px solid #dfe6e9; 
                border-radius: 8px; 
                font-size: 14px; 
                background: #fdfdfd; 
            }
            QLineEdit:focus { 
                border: 1px solid #0984e3; 
                background: white; 
            }
        """)