from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMessageBox

class ReceiptPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        
        # --- החיבור הקריטי ---
        # כאשר לוחצים על אזור הגרירה -> תפעיל את פונקציית פתיחת הקבצים של התצוגה
        self.view.drop_area.clicked_callback = self.view.open_file_dialog
        
        # חיבור כפתורים
        self.view.analyze_btn.clicked.connect(self.analyze_receipt)
        self.view.save_btn.clicked.connect(self.save_transaction)

    def analyze_receipt(self):
        file_path = self.view.drop_area.file_path
        if not file_path:
            QMessageBox.warning(self.view, "שגיאה", "אנא גרור קובץ קבלה או לחץ לבחירה")
            return

        self.view.analyze_btn.setText("מנתח... אנא המתן")
        self.view.analyze_btn.setEnabled(False)
        
        data = self.api_service.upload_receipt(file_path)
        
        self.view.analyze_btn.setText("נתח קבלה עם AI")
        self.view.analyze_btn.setEnabled(True)
        
        if data:
            self.view.merchant_input.setText(data.get("merchant", "לא זוהה"))
            self.view.amount_input.setText(str(data.get("amount", 0)))
            self.view.category_input.setText(data.get("category", "כללי"))
            
            date_str = data.get("date")
            if date_str:
                try:
                    y, m, d = map(int, date_str.split('-'))
                    self.view.date_input.setDate(QDate(y, m, d))
                except: pass
            
            self.view.save_btn.setEnabled(True)
            self.view.save_btn.setText("שמור והוסף להוצאות ✅")
        else:
            QMessageBox.critical(self.view, "שגיאה", "הניתוח נכשל. בדוק חיבור שרת.")

    def save_transaction(self):
        title = self.view.merchant_input.text()
        amount = self.view.amount_input.text()
        category = self.view.category_input.text()
        date = self.view.date_input.date().toString("yyyy-MM-dd")
        
        try:
            amount_float = float(amount)
        except ValueError:
            QMessageBox.warning(self.view, "שגיאה", "הסכום חייב להיות מספר")
            return

        result = self.api_service.add_transaction(title, amount_float, category, date, "ILS")
        
        if result:
            QMessageBox.information(self.view, "הצלחה", "הקבלה נוספה בהצלחה!")
            self.view.merchant_input.clear()
            self.view.amount_input.clear()
            self.view.category_input.clear()
            self.view.save_btn.setEnabled(False)
            self.view.save_btn.setText("שמור והוסף להוצאות")
            # איפוס גם לאזור הגרירה שיראה נקי
            self.view.drop_area.setText("\n\nגרור קובץ קבלה לכאן\nאו לחץ לבחירה\n\n")
            self.view.drop_area.setStyleSheet("""
                QLabel {
                    border: 3px dashed #b2bec3;
                    border-radius: 15px;
                    background-color: #f1f2f6;
                    color: #636e72;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
            self.view.drop_area.file_path = None