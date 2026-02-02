from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    aggregate_id = Column(String, index=True)
    event_type = Column(String)
    payload = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)