from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QFileDialog, QFrame, QLineEdit, QDateEdit, QDoubleSpinBox, QMessageBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap

class DragDropArea(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("\n\nגרור קובץ תמונה לכאן\nאו לחץ לבחירה\n\n")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #a29bfe;
                border-radius: 10px;
                background-color: #f1f2f6;
                color: #636e72;
                font-size: 16px;
            }
            QLabel:hover {
                background-color: #dfe6e9;
                border-color: #6c5ce7;
            }
        """)
        self.setAcceptDrops(True)
        self.file_path = None
        self.clicked_callback = None

    def mousePressEvent(self, event):
        if self.clicked_callback:
            self.clicked_callback()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self.file_path = urls[0].toLocalFile()
            self.setText(f"קובץ נבחר:\n{self.file_path.split('/')[-1]}")
            # כאן אפשר לשדר סיגנל לפרזנטר

class ReceiptView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f6fa;")
        
        main_layout = QHBoxLayout(self)
        
        # --- צד ימין: העלאה ---
        upload_container = QFrame()
        upload_container.setStyleSheet("background-color: white; border-radius: 15px;")
        upload_layout = QVBoxLayout(upload_container)
        
        upload_layout.addWidget(QLabel("סריקת קבלה (AI)"))
        
        self.drop_area = DragDropArea()
        upload_layout.addWidget(self.drop_area)
        
        self.analyze_btn = QPushButton("נתח קבלה")
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.setStyleSheet("background-color: #0984e3; color: white; padding: 10px; border-radius: 5px;")
        upload_layout.addWidget(self.analyze_btn)
        
        main_layout.addWidget(upload_container, 40)

        # --- צד שמאל: תוצאות ועריכה ---
        details_container = QFrame()
        details_container.setStyleSheet("background-color: white; border-radius: 15px;")
        details_layout = QVBoxLayout(details_container)
        
        details_layout.addWidget(QLabel("פרטי העסקה (זוהה אוטומטית)"))
        
        # שם בית העסק
        details_layout.addWidget(QLabel("שם בית העסק:"))
        self.merchant_input = QLineEdit()
        details_layout.addWidget(self.merchant_input)
        
        # תאריך
        details_layout.addWidget(QLabel("תאריך:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        details_layout.addWidget(self.date_input)
        
        # סכום
        details_layout.addWidget(QLabel("סכום (₪):"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(100000)
        details_layout.addWidget(self.amount_input)
        
        # קטגוריה (אופציונלי לשיפור)
        details_layout.addWidget(QLabel("קטגוריה:"))
        self.category_input = QLineEdit()
        details_layout.addWidget(self.category_input)
        
        details_layout.addStretch()
        
        self.save_btn = QPushButton("אשר והוסף להוצאות")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("background-color: #00b894; color: white; padding: 12px; border-radius: 5px; font-weight: bold;")
        self.save_btn.setEnabled(False) # עד שיש ניתוח
        details_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(details_container, 60)

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "בחר תמונה", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.drop_area.file_path = file_name
            self.drop_area.setText(f"קובץ נבחר:\n{file_name.split('/')[-1]}")