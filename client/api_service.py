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