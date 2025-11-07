from sqlalchemy.orm import Session
from models.models import Event
from schemas.event import EventCreate

def create_event(db: Session, event: EventCreate):
    db_event = Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_all_events(db: Session):
    return db.query(Event).all()
