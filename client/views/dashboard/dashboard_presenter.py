from collections import defaultdict
from PySide6.QtCore import QDate
from .dashboard_model import DashboardModel

class DashboardPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        self.model = DashboardModel()
        
        self.view.date_filter.dateChanged.connect(self.on_date_changed)
        self.load_data()

    def on_date_changed(self):
        self.load_data()

    def load_data(self):
        print("Presenter: Fetching dashboard data...")
        data = self.api_service.get_dashboard_data()
        
        if data:
            self.model.total_balance = data.get("total_balance", 0.0)
            self.model.monthly_expenses = data.get("monthly_expenses", 0.0)
            raw_transactions = data.get("recent_transactions", [])
            
            selected_date = self.view.date_filter.date()
            sel_month = selected_date.month()
            sel_year = selected_date.year()

            category_totals = defaultdict(float)
            daily_totals = defaultdict(float)
            
            for t in raw_transactions:
                date_str = t.get("date", "2000-01-01")
                try:
                    y, m, d = map(int, date_str.split('-'))
                    
                    if y == sel_year and m == sel_month:
                        cat = t.get("category", "אחר")
                        amount = t.get("amount_in_ils", 0)
                        category_totals[cat] += amount
                        
                        daily_totals[date_str] += amount
                        
                except:
                    pass

            sorted_categories = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
            
            self.view.update_kpi(self.model.total_balance, self.model.monthly_expenses)
            
            self.view.update_donut_chart(sorted_categories)
            self.view.update_spline_chart(daily_totals)
            
            recent_5 = list(reversed(raw_transactions))[:5]
            self.view.update_recent_table(recent_5)
            
        else:
            print("Error: No data received")