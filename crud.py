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


def delete_note_by_index(db: Session, user_id: str, index: int):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    notes = db.query(Note).filter(
        Note.user_id == user_id,
        Note.created_at >= today,
        Note.created_at < tomorrow
    ).order_by(Note.created_at.asc()).all()

    if 0 <= index < len(notes):
        note_to_delete = notes[index]
        db.delete(note_to_delete)
        db.commit()
        return note_to_delete
    return None

def get_all_notes(db: Session, user_id: str, limit: int = 10):
    return db.query(Note).filter(Note.user_id == user_id).order_by(Note.created_at.desc()).limit(limit).all()

def get_notes_by_specific_date(db: Session, user_id: str, date_str: str):
    try:
        search_date = datetime.strptime(date_str, "%Y-%m-%d")
        start = search_date.replace(hour=0, minute=0, second=0)
        end = search_date.replace(hour=23, minute=59, second=59)
        return db.query(Note).filter(Note.user_id == user_id, Note.created_at.between(start, end)).all()
    except:
        return []