# client/views/budget/budget_presenter.py
from PySide6.QtWidgets import QDialog
# שימוש בייבוא נכון מה-View
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
        data = self.api_service.get_budget_data()
        self.view.clear_all()
        
        if data:
            for b in data.get("budgets", []):
                self.view.add_budget_item(b["name"], b["spent"], b["limit"])
            for s in data.get("subscriptions", []):
                self.view.add_subscription_item(s["name"], s["amount"])
            for g in data.get("savings", []):
                self.view.add_savings_item(g["name"], g["current"], g["target"])

    def handle_add_goal(self):
        dialog = AddGoalDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            name, target = dialog.get_data()
            if name and target > 0:
                if self.api_service.add_savings_goal(name, target):
                    self.view.add_savings_item(name, 0, target)

    def handle_add_budget(self):
        dialog = AddBudgetDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            name, limit = dialog.get_data()
            if name and limit > 0:
                if self.api_service.add_budget_category(name, limit):
                    self.view.add_budget_item(name, 0, limit)

    def handle_add_sub(self):
        dialog = AddSubDialog(self.view)
        if dialog.exec() == QDialog.Accepted:
            name, amount = dialog.get_data()
            if name and amount > 0:
                if self.api_service.add_subscription(name, amount):
                    self.view.add_subscription_item(name, amount)