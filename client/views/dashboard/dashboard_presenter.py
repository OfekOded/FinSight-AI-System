# dashboard_presenter.py - מבקש נתונים מ-ApiService, מעבד אותם לפורמט המתאים לגרפים, ומעדכן את ה-View.


# client/views/dashboard/dashboard_presenter.py
from collections import defaultdict
from PySide6.QtCore import QDate
from .dashboard_model import DashboardModel

class DashboardPresenter:
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        
        # טעינה ראשונית
        self.load_data()

    def load_data(self):
        """פונקציה שטוענת את הנתונים מחדש מהשרת ומעדכנת את המסך"""
        print("Presenter: Refreshing dashboard data...")
        data = self.api_service.get_dashboard_data()
        
        if data:
            total = data.get("total_balance", 0.0)
            monthly = data.get("monthly_expenses", 0.0)
            transactions = data.get("recent_transactions", [])
            
            self.view.update_balance(total)
            self.view.update_monthly_expenses(monthly)
            self.view.update_recent_transactions(transactions)
            self.view.update_chart(data)
        else:
            print("Error: No data received")
    def __init__(self, view, api_service):
        self.view = view
        self.api_service = api_service
        self.model = DashboardModel()
        
        # חיבור שינוי תאריך לפונקציית טעינה
        self.view.date_filter.dateChanged.connect(self.on_date_changed)

    def on_date_changed(self):
        # כשמשנים תאריך, נטען מחדש את הנתונים
        self.load_data()

    def load_data(self):
        print("Presenter: Fetching dashboard data...")
        # כאן אנחנו קוראים לפונקציה בשרת (מניחים שהיא קיימת)
        # בעתיד: אפשר לשלוח את החודש/שנה לשרת כדי לקבל סינון בצד השרת
        # self.api_service.get_dashboard_data(month=..., year=...)
        data = self.api_service.get_dashboard_data()
        
        
        if data:
            self.model.total_balance = data.get("total_balance", 0.0)
            self.model.monthly_expenses = data.get("monthly_expenses", 0.0)
            raw_transactions = data.get("recent_transactions", [])
            
            # --- עיבוד נתונים (Logic) ---
            
            # 1. קבלת החודש והשנה שנבחרו ב-UI
            selected_date = self.view.date_filter.date()
            sel_month = selected_date.month()
            sel_year = selected_date.year()

            # 2. הכנה לגרף דונאט + מיון 
            category_totals = defaultdict(float)
            
            # 3. הכנה לגרף מגמה
            daily_totals = defaultdict(float)
            
            for t in raw_transactions:
                date_str = t.get("date", "2000-01-01")
                try:
                    # המרה פשוטה לבדיקת חודש/שנה
                    y, m, d = map(int, date_str.split('-'))
                    
                    # --- התיקון: בודקים אם העסקה שייכת לחודש הנבחר ---
                    if y == sel_year and m == sel_month:
                        # אם כן, מוסיפים אותה גם לדונאט וגם לגרף היומי
                        
                        # לדונאט:
                        cat = t.get("category", "אחר")
                        amount = t.get("amount_in_ils", 0)
                        category_totals[cat] += amount
                        
                        # לגרף היומי:
                        daily_totals[date_str] += amount
                        
                except:
                    pass
            

            # מיון קטגוריות מהגדול לקטן
            sorted_categories = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
            
            # --- עדכון התצוגה ---
            self.view.update_kpi(self.model.total_balance, self.model.monthly_expenses)
            
            # שליחת הנתונים המסוננים לגרפים
            self.view.update_donut_chart(sorted_categories)
            self.view.update_spline_chart(daily_totals)
            
            # עדכון טבלה (כאן נשאיר את ה-5 האחרונות בכללי, או שאפשר לסנן גם אותן אם תרצה)
            recent_5 = list(reversed(raw_transactions))[:5]
            self.view.update_recent_table(recent_5)
            
        else:
            print("Error: No data received")