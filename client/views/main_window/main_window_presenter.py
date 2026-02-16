from views.dashboard.dashboard_view import DashboardView
from views.dashboard.dashboard_presenter import DashboardPresenter

from views.transactions.transaction_view import TransactionView
from views.transactions.transaction_presenter import TransactionPresenter

from views.budget.budget_view import BudgetView
from views.budget.budget_presenter import BudgetPresenter

from views.ai_agent.agent_view import AgentView
from views.ai_agent.agent_presenter import AgentPresenter

from ..profile.profile_view import ProfileView
from ..profile.profile_presenter import ProfilePresenter

from ..receipts.receipt_view import ReceiptView
from ..receipts.receipt_presenter import ReceiptPresenter

from .main_window_model import MainWindowModel

class MainWindowPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        self.model = MainWindowModel()
        
        self.dashboard_view = DashboardView()
        self.dashboard_presenter = DashboardPresenter(self.dashboard_view, self.api_service)
        
        self.budget_view = BudgetView()
        self.budget_presenter = BudgetPresenter(self.budget_view, self.api_service)
        
        self.trans_view = TransactionView()
        self.trans_presenter = TransactionPresenter(self.trans_view, self.api_service)
        
        self.agent_view = AgentView()
        self.agent_presenter = AgentPresenter(self.agent_view, self.api_service)
        
        self.receipt_view = ReceiptView()
        self.receipt_presenter = ReceiptPresenter(self.receipt_view, self.api_service)

        self.profile_view = ProfileView()
        self.profile_presenter = ProfilePresenter(self.profile_view, self.api_service)
        
        self.view.content_area.addWidget(self.dashboard_view)
        self.view.content_area.addWidget(self.budget_view)    
        self.view.content_area.addWidget(self.trans_view)     
        self.view.content_area.addWidget(self.agent_view)     
        self.view.content_area.addWidget(self.receipt_view)
        self.view.content_area.addWidget(self.profile_view)
        
        # חיבור הסיגנל מהפרופיל לדשבורד - כשמתעדכן הפרופיל, נטען מחדש את הדשבורד
        self.profile_presenter.profile_updated.connect(self.dashboard_presenter.load_data)
        
        self.view.btn_dashboard.clicked.connect(lambda: self.switch_view(0))
        self.view.btn_budget.clicked.connect(lambda: self.switch_view(1))        
        self.view.btn_add_transaction.clicked.connect(lambda: self.switch_view(2))
        self.view.btn_ai_chat.clicked.connect(lambda: self.switch_view(3))
        self.view.btn_receipts.clicked.connect(lambda: self.switch_view(4))
        self.view.btn_profile.clicked.connect(lambda: self.switch_view(5))
        
        self.view.btn_dashboard.setChecked(True)
        self.switch_view(0)

    def switch_view(self, index):
        self.model.current_view_index = index 
        self.view.content_area.setCurrentIndex(index)
        
        if index == 0:
            self.dashboard_presenter.load_data()
        elif index == 1:
            self.budget_presenter.load_data()