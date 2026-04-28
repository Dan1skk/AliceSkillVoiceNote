from sqlalchemy.orm import Session
from models import Note
from datetime import datetime, timedelta

def create_note(db: Session, user_id: str, content: str, attachment: str = None):
    db_note = Note(user_id=user_id, content=content, attachment_url=attachment)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes_by_date(db: Session, user_id: str, date: datetime):
    start = date.replace(hour=0, minute=0, second=0)
    end = date.replace(hour=23, minute=59, second=59)
    return db.query(Note).filter(Note.user_id == user_id, Note.created_at.between(start, end)).all()

def delete_last_note(db: Session, user_id: str):
    note = db.query(Note).filter(Note.user_id == user_id).order_by(Note.id.desc()).first()
    if note:
        db.delete(note)
        db.commit()
        return note
    return None