from PySide6.QtCore import QObject, Signal

class ProfilePresenter(QObject):
    # הגדרת הסיגנל
    profile_updated = Signal()

    def __init__(self, view, api_service):
        super().__init__() # אתחול QObject
        self.view = view
        self.api_service = api_service
        
        self.view.save_btn.clicked.connect(self.save_profile)

    def save_profile(self):
        new_name = self.view.name_input.text().strip()
        salary = self.view.salary_input.value()
        password = self.view.password_input.text()
        
        current_name = self.view.card_name.lbl_value.text()
        final_name = new_name if new_name else current_name
        
        if not final_name or final_name == "אורח":
             self.view.show_message("שגיאה", "חובה שיהיה שם למשתמש", is_error=True)
             return

        success = self.api_service.update_user_profile(salary, final_name, password)

        if success:
            self.view.update_display(final_name, salary)
            self.view.show_message("הצלחה", "הפרופיל עודכן בהצלחה!")
            self.view.name_input.clear()
            self.view.password_input.clear()
            
            # --- כאן הקסם קורה: שליחת הודעה לכל המערכת להתעדכן ---
            print("Profile updated! Emitting signal...")
            self.profile_updated.emit()
            
        else:
            self.view.show_message("שגיאה", "לא ניתן לשמור את השינויים כרגע.", is_error=True)