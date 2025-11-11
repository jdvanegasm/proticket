from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.event import EventCreate, EventOut, EventUpdate
from crud import crud_event

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Crear un nuevo evento"""
    return crud_event.create_event(db, event)

@router.get("/", response_model=list[EventOut])
def get_events(db: Session = Depends(get_db)):
    """Obtener todos los eventos"""
    return crud_event.get_all_events(db)

@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Obtener un evento por ID"""
    event = crud_event.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, event: EventUpdate, db: Session = Depends(get_db)):
    """Actualizar un evento existente"""
    db_event = crud_event.get_event_by_id(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Actualizar solo los campos que se enviaron
    update_data = event.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Eliminar un evento"""
    deleted = crud_event.delete_event(db, event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully", "deleted_event_id": event_id}

@router.put("/{event_id}", response_model=EventOut)
def update_event_full(event_id: int, event_data: EventCreate, db: Session = Depends(get_db)):
    db_event = crud_event.get_event_by_id(db, event_id)
    if not db_event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    
    # Actualizar todos los campos
    for key, value in event_data.model_dump().items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event