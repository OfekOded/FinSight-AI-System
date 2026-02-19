from PySide6.QtWidgets import QDialog, QMessageBox, QProgressBar
from .dialogs.savings_action_dialog import SavingsActionDialog
from .budget_view import AddGoalDialog, AddBudgetDialog, AddSubDialog

class BudgetPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        
        # חיבור כל הכפתורים
        self.view.add_goal_btn.clicked.connect(self.handle_add_goal)
        self.view.add_budget_btn.clicked.connect(self.handle_add_budget)
        self.view.add_sub_btn.clicked.connect(self.handle_add_sub)
        
        self.load_data()

    def load_data(self):
        print("Presenter: Fetching budget data...")
        try:
            self.view.clear_all()
        except Exception as e:
            print(f"Error clearing layout: {e}")
        
        data = self.api_service.get_budget_data()
        
        if not data:
            print("Failed to load budget data")
            return
        
        try:
            for b in data.get("budgets", []):
                limit = b.get("limit_amount", 0)
                spent = b.get("spent_amount", 0)
                self.view.add_budget_item(b["name"], spent, limit)
                
            for s in data.get("subscriptions", []):
                sub_id = s.get("id")
                del_btn = self.view.add_subscription_item(sub_id, s["name"], s["amount"])
                del_btn.clicked.connect(lambda checked=False, sid=sub_id, snames=s["name"]: self.handle_delete_sub(sid, snames))
                
            for g in data.get("savings", []):
                target = g.get("target_amount", 0)
                current = g.get("current_amount", 0)
                goal_id = g.get("id") or 0
                
                item_widget = self.view.add_savings_item(goal_id, g["name"], current, target)
                item_widget.clicked.connect(self.handle_savings_click)
        except Exception as e:
            print(f"Error loading budget data: {e}")

    def handle_savings_click(self, goal_id, name, current, target):
        """פתיחת הדיאלוג החכם"""
        dialog = SavingsActionDialog(self.view, name, current, target)
        if dialog.exec() == QDialog.Accepted:
            action = dialog.action
            
            if action == 'deposit':
                amount = dialog.amount_to_add
                if self.api_service.deposit_to_savings(goal_id, amount):
                    QMessageBox.information(self.view, "הצלחה", f"הוספת {amount} ₪ לחיסכון בהצלחה!")
                    self.load_data() # רענון
            
            elif action == 'finish':
                # סיום יעד = מחיקה ללא החזר (הכסף בוזבז)
                if self.api_service.delete_savings_goal(goal_id, refund=False):
                    QMessageBox.information(self.view, "מזל טוב!", "היעד הושלם בהצלחה!")
                    self.load_data()

            elif action == 'cancel':
                # ביטול יעד = מחיקה עם החזר (הכסף חוזר)
                if self.api_service.delete_savings_goal(goal_id, refund=True):
                    QMessageBox.information(self.view, "בוטל", "היעד בוטל והכסף הוחזר ליתרה.")
                    self.load_data()
    
    def handle_add_goal(self):
        dialog = AddGoalDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            name, target = dialog.get_data()
            if name and target > 0:
                if self.api_service.add_savings_goal(name, target):
                    self.load_data()

    def handle_add_budget(self):
        dialog = AddBudgetDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            name, limit = dialog.get_data()
            if name and limit > 0:
                if self.api_service.add_budget_category(name, limit):
                    self.load_data()

    def handle_add_sub(self):
        dialog = AddSubDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            name, amount = dialog.get_data()
            if name and amount > 0:
                if self.api_service.add_subscription(name, amount):
                    self.load_data()
                    
    def handle_delete_sub(self, sub_id, name):
        reply = QMessageBox.question(
            self.view, 
            "ביטול מנוי", 
            f"האם אתה בטוח שברצונך למחוק את המנוי '{name}'?\n\nשימו לב: המחיקה תעצור חיובים עתידיים, אך לא תזכה אתכם על התשלום שכבר בוצע החודש.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.api_service.delete_subscription(sub_id):
                QMessageBox.information(self.view, "הצלחה", "המנוי הוסר בהצלחה!")
                self.load_data() # טוען מחדש את המסך כדי להעלים את המנוי מהרשימה
            else:
                QMessageBox.warning(self.view, "שגיאה", "שגיאה במחיקת המנוי.")