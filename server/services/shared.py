from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
import hashlib
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db
from models import User

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401)
    try:
        if "-" in authorization:
            user_id = authorization.split("-")[1]
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise HTTPException(status_code=401)
            return user
        else:
            raise HTTPException(status_code=401)
    except Exception:
        raise HTTPException(status_code=401)