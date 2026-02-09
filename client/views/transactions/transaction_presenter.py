# transaction_presenter.py - מקבל את לחיצת ה"שמור", בודק תקינות, ושולח את הנתונים לשרת דרך ה-ApiService.
class TransactionPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        
        # חיבור כפתור השמירה לפונקציה
        self.view.save_btn.clicked.connect(self.handle_save)

    def handle_save(self):
        data = self.view.get_data()
        
        # בדיקות תקינות (Validation)
        if not data["title"] or not data["amount"]:
            self.view.show_message("שגיאה", "נא למלא את כל שדות החובה", is_error=True)
            return

        try:
            amount = float(data["amount"])
        except ValueError:
            self.view.show_message("שגיאה", "הסכום חייב להיות מספר", is_error=True)
            return

        # שליחה לשרת
        print(f"Sending transaction: {data}")
        response = self.api_service.add_transaction(
            title=data["title"],
            amount=amount,
            category=data["category"],
            date=data["date"]
        )

        if response:
            self.view.show_message("הצלחה", "העסקה נשמרה בהצלחה!")
            self.view.clear_form()
        else:
            self.view.show_message("שגיאה", "שגיאה בתקשורת עם השרת", is_error=True)