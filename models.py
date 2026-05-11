from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

# Модель записи дневника
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)           # ID пользователя Алисы
    content = Column(String)           # Текст записи
    attachment_url = Column(String, nullable=True)  # Ссылка на вложение (опционально)
    created_at = Column(DateTime, default=datetime.now)
