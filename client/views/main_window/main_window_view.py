import os
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinSight AI System")
        self.resize(1100, 750)
        
        # נתיב בסיס לאייקונים
        self.icons_path = os.path.join(os.path.dirname(__file__), '../../assets/icons')

        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        self.main_layout = QHBoxLayout(main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #1e272e; 
                min-width: 250px;
                border: none;
            }
        """)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_layout.setSpacing(10)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 20)
        
        # --- כפתורי התפריט ---
        self.btn_dashboard = self.create_nav_button("לוח בקרה", "dashboard.svg")
        self.btn_budget = self.create_nav_button("תקציב ויעדים", "budget.svg") 
        self.btn_add_transaction = self.create_nav_button("הוספת עסקה", "transaction.svg")
        self.btn_ai_chat = self.create_nav_button("התייעצות AI", "ai.svg")
        self.btn_receipts = self.create_nav_button("סריקת קבלה", "receipts.svg") 
        self.btn_profile = self.create_nav_button("אזור אישי", "profile.svg")
        
        self.sidebar_layout.addWidget(self.btn_dashboard)
        self.sidebar_layout.addWidget(self.btn_budget) 
        self.sidebar_layout.addWidget(self.btn_add_transaction)
        self.sidebar_layout.addWidget(self.btn_receipts)
        self.sidebar_layout.addWidget(self.btn_ai_chat)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.btn_profile)
        
        # --- Content ---
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #f1f2f6;")
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)

    def create_nav_button(self, text, icon_filename):
        btn = QPushButton(text) 
        btn.setCursor(Qt.PointingHandCursor)
        
        btn.setLayoutDirection(Qt.RightToLeft)
        
        # טעינת האייקון
        icon_path = os.path.join(self.icons_path, icon_filename)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(32, 32))
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #d2dae2;
                text-align: left;
                padding-right: 10px;
                padding-left: 10px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-size: 16px;
                border-radius: 0px; 
                border: none;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #2f3640;
                color: white;
                border-right: 5px solid #00d2d3;
                text-align: left;
            }
            QPushButton:checked {
                background-color: #2f3640;
                color: #00d2d3;
                font-weight: bold;
                border-right: 5px solid #00d2d3;
                text-align: left;
            }
        """)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        return btn