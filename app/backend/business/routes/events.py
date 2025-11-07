from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import SessionLocal
from schemas.event import EventCreate, EventOut
from crud import crud_event
from services.auth_service import get_user_info

router = APIRouter(prefix="/events", tags=["Events"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    user_info = get_user_info(str(event.organizer_id))
    if not user_info or user_info["role"] != "organizer":
        raise HTTPException(status_code=403, detail="User not authorized to create events")
    return crud_event.create_event(db, event)
