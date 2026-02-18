# client/api_service.py
import requests

class ApiService:
    def __init__(self):
        # כתובת השרת
        self.base_url = "http://127.0.0.1:8000/api"
        # נשמור את הטוקן אם נצטרך אותו בעתיד לבקשות מאובטחות
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
        
    # def get_user_profile(self):
    #     url = f"{self.base_url}/auth/profile/me"
    #     try:
    #         response = requests.get(url, headers=self._get_headers())
    #         response.raise_for_status()
    #         return response.json() # מחזיר {username, full_name, salary}
    #     except Exception as e:
    #         print(f"Fetch profile failed: {e}")
    #         return None
        
    def update_user_profile(self, salary, full_name, password=None):
        url = f"{self.base_url}/user/profile"
        payload = {
            "salary": float(salary) if salary else 0.0,
            "full_name": full_name,
            "password": password
        }
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return True
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
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None

    def update_user_profile(self, salary=None, full_name=None, current_password=None, new_password=None):
        """עדכון פרופיל"""
        url = f"{self.base_url}/auth/profile/update"
        payload = {}
        if salary is not None: payload["salary"] = salary
        if full_name: payload["full_name"] = full_name
        if new_password:
            payload["current_password"] = current_password
            payload["new_password"] = new_password
            
        try:
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                return True, "הפרופיל עודכן בהצלחה"
            else:
                return False, res.json().get("detail", "שגיאה בעדכון")
        except Exception as e:
            return False, str(e)

    def upload_receipt(self, file_path):
        url = f"{self.base_url}/receipts/analyze"
        try:
            with open(file_path, 'rb') as f:
                # We send the file as 'file' to match the FastAPI 'file: UploadFile' parameter
                files = {'file': (file_path.split('/')[-1], f, 'image/png')}
                
                # Use self._get_headers(content_type=None) so 'requests' can set the multipart boundary
                response = requests.post(url, files=files, headers=self._get_headers(content_type=None))
                
                response.raise_for_status()
                return response.json() # This will return the real data from Gemini
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
            response = requests.get(f"{self.base_url}/budget", headers=self._get_headers())
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