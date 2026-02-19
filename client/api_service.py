# client/api_service.py
import os
import requests
import mimetypes

class ApiService:
    def __init__(self):
        # כתובת השרת
        self.base_url = "http://127.0.0.1:8000/api"
        self.auth_token = None

    def _get_headers(self, content_type="application/json"):
        """פונקציית עזר להוספת הטוקן לכל בקשה"""
        headers = {}
        if content_type:
            headers["Content-Type"] = content_type
        if self.auth_token:
            headers["Authorization"] = self.auth_token
        return headers
    
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
            data = response.json()
            
            if "token" in data:
                self.auth_token = data["token"]
                return data
            
            return data
        
        except requests.exceptions.RequestException as e:
            print(f"Registration failed: {e}")
            return None
        
    def update_user_profile(self, salary, full_name, current_password=None, new_password=None):
        url = f"{self.base_url}/user/profile" # תיקון: נתיב אחיד לפי השרת
        payload = {}
        if salary is not None: payload["salary"] = float(salary)
        if full_name: payload["full_name"] = full_name
        if new_password:
            # השרת כרגע מצפה רק לסיסמה חדשה (לפי הקוד ששלחת), הוספתי תמיכה בזה
            payload["new_password"] = new_password
        
        try:
            # תיקון: הוספת headers
            res = requests.post(url, json=payload, headers=self._get_headers())
            if res.status_code == 200:
                return True
            else:
                return False
        
        except Exception as e:
            print(f"Update profile failed: {e}")
            return False
        
    def get_dashboard_data(self):
        try:
            response = requests.get(f"{self.base_url}/dashboard", headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching dashboard: {e}")
            return None

    def get_user_profile(self):
        """שליפת פרטי המשתמש הנוכחי"""
        url = f"{self.base_url}/auth/profile/me"
        try:
            # תיקון: שימוש ב-_get_headers כדי לשלוח את הטוקן
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None

    def upload_receipt(self, file_path):
        url = f"{self.base_url}/receipts/analyze"
        try:
            if not os.path.exists(file_path): return None
            
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
                
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.split('/')[-1], f, mime_type)}
                headers = {}
                if self.auth_token:
                    headers["Authorization"] = self.auth_token
                
                response = requests.post(url, files=files, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error uploading receipt: {e}")
            return None
        
    def add_transaction(self, title, amount, category, date, currency="ILS"):
        payload = {
            "title": title,
            "amount": amount,
            "category": category,
            "date": date,
            "currency": currency
        }
        try:
            response = requests.post(f"{self.base_url}/transactions", json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error adding transaction: {e}")
            return None


    def add_budget_category(self, name, limit):
        payload = {"name": name, "limit_amount": limit}
        try:
            response = requests.post(f"{self.base_url}/budget/category", json=payload, headers=self._get_headers())
            response.raise_for_status()
            return True
        except Exception:
            return False

    def add_subscription(self, name, amount):
        payload = {"name": name, "amount": amount}
        try:
            response = requests.post(f"{self.base_url}/budget/subscription", json=payload, headers=self._get_headers())
            response.raise_for_status()
            return True
        except Exception:
            return False
        
    def get_budget_data(self):
        """שליפת נתוני תקציב"""
        try:
            response = requests.get(f"{self.base_url}/budget", headers=self._get_headers())
            return response.json()
        except Exception as e:
            print(f"Server error (get_budget): {e}")

            return {"budgets": [], "subscriptions": [], "savings": []}

    def add_savings_goal(self, name, target):
        """שליחת יעד חדש לשרת"""
        payload = {"name": name, "target": target, "current": 0}
        try:
            # מנסים לשלוח לשרת
            response = requests.post(f"{self.base_url}/budget/savings", json=payload, headers=self._get_headers())
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Server error (add_goal): {e}")
            return False
        
    def deposit_to_savings(self, goal_id, amount):
        """הוספת כסף לחיסכון"""
        try:
            url = f"{self.base_url}/budget/savings/{goal_id}/deposit?amount={amount}"
            res = requests.put(url, headers=self._get_headers())
            return res.status_code == 200
        except Exception as e:
            print(f"Error depositing: {e}")
            return False

    def delete_savings_goal(self, goal_id, refund=False):
        """מחיקת חיסכון (עם אופציה להחזר כספי)"""
        try:
            url = f"{self.base_url}/budget/savings/{goal_id}?refund={str(refund).lower()}"
            res = requests.delete(url, headers=self._get_headers())
            return res.status_code == 200
        except Exception as e:
            print(f"Error deleting goal: {e}")
            return False
        
    def consult_ai(self, question, history=None):
            if history is None:
                history = []
            url = f"{self.base_url}/ai/consult"
            payload = {"question": question, "history": history}
            try:
                response = requests.post(url, json=payload, headers=self._get_headers())
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException:
                return None