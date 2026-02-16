from PySide6.QtCore import QDate

class ReceiptPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        
        # חיבורים
        self.view.drop_area.clicked_callback = self.view.open_file_dialog
        self.view.analyze_btn.clicked.connect(self.analyze_receipt)
        self.view.save_btn.clicked.connect(self.save_transaction)

    def analyze_receipt(self):
        file_path = self.view.drop_area.file_path
        if not file_path:
            # הודעת שגיאה אם לא נבחר קובץ
            return

        self.view.analyze_btn.setText("מנתח... אנא המתן")
        self.view.analyze_btn.setEnabled(False)
        
        # קריאה לשרת (כולל ה-Mock שעשינו ב-ApiService)
        data = self.api_service.upload_receipt(file_path)
        
        self.view.analyze_btn.setText("נתח קבלה")
        self.view.analyze_btn.setEnabled(True)
        
        if data:
            # מילוי השדות בתוצאה
            self.view.merchant_input.setText(data.get("merchant", ""))
            self.view.amount_input.setValue(data.get("amount", 0))
            self.view.category_input.setText(data.get("category", "כללי"))
            
            date_str = data.get("date")
            if date_str:
                # הנחה שהתאריך מגיע כ YYYY-MM-DD
                try:
                    y, m, d = map(int, date_str.split('-'))
                    self.view.date_input.setDate(QDate(y, m, d))
                except:
                    pass
            
            self.view.save_btn.setEnabled(True)

    def save_transaction(self):
        # איסוף הנתונים מהטופס
        title = self.view.merchant_input.text()
        amount = self.view.amount_input.value()
        category = self.view.category_input.text()
        date = self.view.date_input.date().toString("yyyy-MM-dd")
        
        # שליחה לשרת (שימוש בפונקציה הקיימת להוספת עסקה)
        # שים לב: אנחנו משתמשים בפונקציה הקיימת ב-API להוספת טרנזקציה רגילה
        result = self.api_service.add_transaction(title, amount, category, date)
        
        if result:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self.view, "הצלחה", "הקבלה נוספה בהצלחה להוצאות!")
            # איפוס
            self.view.merchant_input.clear()
            self.view.amount_input.setValue(0)
            self.view.save_btn.setEnabled(False)
            self.view.drop_area.setText("\n\nגרור קובץ תמונה לכאן\nאו לחץ לבחירה\n\n")