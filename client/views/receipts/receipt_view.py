from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFrame, QFileDialog, QSizePolicy)
from PySide6.QtCore import Qt, QDate

# ייבוא הרכיבים
from components.drag_drop import DragDropArea
from components.inputs import ModernDateEdit, ModernInput

class ReceiptView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- כותרת ---
        header = QWidget()
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #dfe6e9; padding: 15px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("סריקת וניתוח קבלות (AI Vision)")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #2d3436;")
        header_layout.addWidget(title)
        self.layout.addWidget(header)

        # --- תוכן ראשי ---
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)

        # --- צד ימין: גרירה (גדול) ---
        right_panel = QVBoxLayout()
        
        self.drop_area = DragDropArea()
        self.drop_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        right_panel.addWidget(self.drop_area)
        content_layout.addLayout(right_panel, stretch=2)

        # --- צד שמאל: טופס (צר) ---
        form_frame = QFrame()
        form_frame.setFixedWidth(380)
        form_frame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 15px; border: 1px solid #dfe6e9; }
            QLabel { font-weight: bold; color: #636e72; margin-top: 10px; border: none; }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setAlignment(Qt.AlignTop)

        form_title = QLabel("פרטי העסקה")
        form_title.setStyleSheet("font-size: 20px; color: #2d3436; margin-bottom: 5px; border: none;")
        form_layout.addWidget(form_title)
        
        form_subtitle = QLabel("הנתונים יתמלאו אוטומטית ע\"י ה-AI")
        form_subtitle.setStyleSheet("font-size: 13px; color: #b2bec3; margin-bottom: 20px; font-weight: normal; border: none;")
        form_layout.addWidget(form_subtitle)

        # שדות
        form_layout.addWidget(QLabel("שם בית העסק:"))
        self.merchant_input = ModernInput("למשל: סופר-פארם")
        form_layout.addWidget(self.merchant_input)

        form_layout.addWidget(QLabel("סכום לתשלום:"))
        self.amount_input = ModernInput("0.00")
        form_layout.addWidget(self.amount_input)
        
        form_layout.addWidget(QLabel("תאריך:"))
        self.date_input = ModernDateEdit()
        self.date_input.setDate(QDate.currentDate())
        form_layout.addWidget(self.date_input)

        form_layout.addWidget(QLabel("קטגוריה:"))
        self.category_input = ModernInput("למשל: מזון / דלק")
        form_layout.addWidget(self.category_input)

        form_layout.addSpacing(20)

        # כפתורים
        self.analyze_btn = QPushButton("✨ נתח קבלה עם AI")
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.setStyleSheet("""
            QPushButton { 
                background-color: #6c5ce7; color: white; border-radius: 8px; 
                padding: 12px; font-weight: bold; font-size: 15px; border: none;
            }
            QPushButton:hover { background-color: #5f3dc4; }
        """)
        form_layout.addWidget(self.analyze_btn)

        self.save_btn = QPushButton("שמור והוסף להוצאות")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton { 
                background-color: #00b894; color: white; border-radius: 8px; 
                padding: 12px; font-weight: bold; font-size: 15px; margin-top: 10px; border: none;
            }
            QPushButton:hover { background-color: #00a884; }
            QPushButton:disabled { background-color: #b2bec3; }
        """)
        form_layout.addWidget(self.save_btn)
        
        form_layout.addStretch()

        content_layout.addWidget(form_frame)
        self.layout.addWidget(content_container)

    def open_file_dialog(self):
        """פותח חלון לבחירת קובץ ומעדכן את אזור הגרירה"""
        file_name, _ = QFileDialog.getOpenFileName(self, "בחר תמונה", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.drop_area.set_file(file_name)