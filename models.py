from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    content = Column(String)
    attachment_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)