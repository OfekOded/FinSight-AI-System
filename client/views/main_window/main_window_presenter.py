from views.dashboard.dashboard_view import DashboardView
from views.dashboard.dashboard_presenter import DashboardPresenter
from views.transactions.transaction_view import TransactionView
from views.transactions.transaction_presenter import TransactionPresenter
from .main_window_model import MainWindowModel 

class MainWindowPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        self.model = MainWindowModel() 
        
        # 1. דשבורד
        self.dashboard_view = DashboardView()
        self.dashboard_presenter = DashboardPresenter(self.dashboard_view, self.api_service)
        
        # 2. הוספת עסקה
        self.trans_view = TransactionView()
        self.trans_presenter = TransactionPresenter(self.trans_view, self.api_service)
        
        # הוספה ל-Stack
        self.view.content_area.addWidget(self.dashboard_view)
        self.view.content_area.addWidget(self.trans_view)
        
        # חיבור כפתורים
        self.view.btn_dashboard.clicked.connect(lambda: self.switch_view(0))
        self.view.btn_add_transaction.clicked.connect(lambda: self.switch_view(1))
        
        # התחלה
        self.view.btn_dashboard.setChecked(True)
        self.switch_view(0)

    def switch_view(self, index):
        # עדכון המודל
        self.model.current_view_index = index 
        
        # עדכון התצוגה
        self.view.content_area.setCurrentIndex(index)
        
        if index == 0:
            self.dashboard_presenter.load_data()