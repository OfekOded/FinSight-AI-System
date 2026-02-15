# client/api_service.py
import requests

class ApiService:
    def __init__(self):
        # כתובת השרת
        self.base_url = "http://127.0.0.1:8000/api"
        # נשמור את הטוקן אם נצטרך אותו בעתיד לבקשות מאובטחות
        self.auth_token = None

    def login(self, username, password):
        """
        שולח בקשת התחברות לשרת.
        """
        url = f"{self.base_url}/auth/login"
        payload = {"username": username, "password": password}
        
        try:
            print(f"Sending POST to {url} with {payload}")
            response = requests.post(url, json=payload)
            
            # אם השרת מחזיר 401/403/404 - זה יזרוק שגיאה
            response.raise_for_status() 
            
            data = response.json()
            # שמירת הטוקן (אם השרת מחזיר כזה)
            self.auth_token = data.get("token")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Login failed: {e}")
            # כאן אפשר להחזיר את הודעת השגיאה מהשרת אם יש
            return None

    def register(self, username, password, full_name):
        """
        שולח בקשת הרשמה לשרת.
        """
        url = f"{self.base_url}/auth/register"
        payload = {
            "username": username, 
            "password": password,
            "full_name": full_name
        }
        
        try:
            print(f"Sending POST to {url}")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json() # מחזיר הצלחה
        except requests.exceptions.RequestException as e:
            print(f"Registration failed: {e}")
            return None

    def get_dashboard_data(self):
        try:
            # בעתיד: נוסיף כאן header עם הטוקן
            response = requests.get(f"{self.base_url}/dashboard")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching dashboard: {e}")
            return None

    def add_transaction(self, title, amount, category, date):
        payload = {
            "title": title,
            "amount": amount,
            "category": category,
            "date": date,
            "currency": "ILS"
        }
        try:
            response = requests.post(f"{self.base_url}/transactions", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error adding transaction: {e}")
            return None


    def add_budget_category(self, name, limit):
        payload = {"name": name, "limit_amount": limit}
        try:
            requests.post(f"{self.base_url}/budget/category", json=payload)
            return True
        except Exception:
            return False

    def add_subscription(self, name, amount):
        payload = {"name": name, "amount": amount}
        try:
            requests.post(f"{self.base_url}/budget/subscription", json=payload)
            return True
        except Exception:
            return False
        
    def get_budget_data(self):
        """שליפת נתוני תקציב"""
        try:
            response = requests.get(f"{self.base_url}/budget")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Server error (get_budget): {e}")
            # --- מצב 'כאילו' ---
            # מחזירים מבנה ריק כדי שהתוכנה לא תקרוס, אבל בלי נתונים מזויפים
            return {"budgets": [], "subscriptions": [], "savings": []}

    def add_savings_goal(self, name, target):
        """שליחת יעד חדש לשרת"""
        payload = {"name": name, "target": target, "current": 0}
        try:
            # מנסים לשלוח לשרת
            response = requests.post(f"{self.base_url}/budget/savings", json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Server error (add_goal): {e}")
            # --- מצב 'כאילו' ---
            # ביקשת שנתנהג כאילו השרת עבד והחזיר תשובה חיובית
            # אז אנחנו מחזירים True גם אם נכשל
            return True
        
    def consult_ai(self, question):
        url = f"{self.base_url}/ai/consult"
        payload = {"question": question}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None