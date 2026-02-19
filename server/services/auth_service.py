from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine, Base, get_db
from models import User
from schemas import UserRegister, UserLogin, AuthResponse, UserProfileUpdate
from services.shared import get_current_user, hash_password

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/api/auth/register", response_model=AuthResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400)
    new_user = User(username=user.username, full_name=user.full_name, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"token": f"token-{new_user.id}", "username": new_user.username, "status": "created"}

@app.post("/api/auth/login", response_model=AuthResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.password_hash != hash_password(user.password):
        raise HTTPException(status_code=401)
    return {"token": f"token-{db_user.id}", "username": db_user.username, "status": "logged_in"}

@app.get("/api/auth/profile/me")
def get_my_profile(user: User = Depends(get_current_user)):
    return {"username": user.username, "full_name": user.full_name, "salary": user.salary}

@app.post("/api/user/profile")
def update_user_profile(update_data: UserProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if update_data.salary is not None:
        user.salary = update_data.salary
    if update_data.full_name:
        user.full_name = update_data.full_name
    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(status_code=400)
        if user.password_hash != hash_password(update_data.current_password):
            raise HTTPException(status_code=401)
        user.password_hash = hash_password(update_data.new_password)
    db.commit()
    return {"status": "success", "salary": user.salary, "full_name": user.full_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)