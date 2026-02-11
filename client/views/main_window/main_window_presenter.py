from views.dashboard.dashboard_view import DashboardView
from views.dashboard.dashboard_presenter import DashboardPresenter

from views.transactions.transaction_view import TransactionView
from views.transactions.transaction_presenter import TransactionPresenter

from views.budget.budget_view import BudgetView
from views.budget.budget_presenter import BudgetPresenter

from .main_window_model import MainWindowModel

class MainWindowPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        self.model = MainWindowModel()
        
        # --- 1. דשבורד (Index 0) ---
        self.dashboard_view = DashboardView()
        self.dashboard_presenter = DashboardPresenter(self.dashboard_view, self.api_service)
        
        # --- 2. תקציב ויעדים (Index 1) ---
        self.budget_view = BudgetView()
        self.budget_presenter = BudgetPresenter(self.budget_view, self.api_service)
        
        # --- 3. הוספת עסקה (Index 2) ---
        self.trans_view = TransactionView()
        self.trans_presenter = TransactionPresenter(self.trans_view, self.api_service)
        
        # הוספה ל-Stack (הסדר קובע את האינדקס!)
        self.view.content_area.addWidget(self.dashboard_view) # 0
        self.view.content_area.addWidget(self.budget_view)    # 1
        self.view.content_area.addWidget(self.trans_view)     # 2
        
        # חיבור כפתורים לפונקציית החלפה
        self.view.btn_dashboard.clicked.connect(lambda: self.switch_view(0))
        self.view.btn_budget.clicked.connect(lambda: self.switch_view(1))        # <--- חדש
        self.view.btn_add_transaction.clicked.connect(lambda: self.switch_view(2))
        
        # התחלה: מסך הבית
        self.view.btn_dashboard.setChecked(True)
        self.switch_view(0)

    def switch_view(self, index):
        self.model.current_view_index = index 
        self.view.content_area.setCurrentIndex(index)
        
        # טעינת נתונים רלוונטיים כשנכנסים למסך
        if index == 0:
            self.dashboard_presenter.load_data()
        elif index == 1:
            self.budget_presenter.load_data() # <--- טעינת נתונים לתקציב