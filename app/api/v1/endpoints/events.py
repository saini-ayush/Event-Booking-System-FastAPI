from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ....database import get_db
from ....models.event import Event as EventModel
from ....schemas.event import Event, EventCreate, EventUpdate
from ....core.security import get_current_admin
from ....models.user import User

router = APIRouter()

# Admin
@router.post(
    "/admin/events",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)]
)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    db_event = EventModel(
        **event.model_dump(),
        available_tickets=event.total_tickets
    )

    if db_event.date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event date must be in the future"
        )
    db.add(db_event)
    try:
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating event"
        )
    return db_event

@router.put(
    "/admin/events/{event_id}",
    response_model=Event,
    dependencies=[Depends(get_current_admin)]
)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db)
):
    db_event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "total_tickets":
            ticket_difference = value - db_event.total_tickets
            db_event.available_tickets += ticket_difference
        setattr(db_event, key, value)

    try:
        db.commit()
        db.refresh(db_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating event"
        )
    return db_event

@router.delete(
    "/admin/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)]
)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    db_event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    try:
        db.delete(db_event)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting event"
        )
    return None

@router.get(
    "/admin/events",
    response_model=List[Event],
    dependencies=[Depends(get_current_admin)]
)
async def get_all_events_admin(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    events = db.query(EventModel).offset(skip).limit(limit).all()
    return events

# User
@router.get("/events", response_model=List[Event])
async def get_available_events(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    events = db.query(EventModel).filter(
        EventModel.available_tickets > 0,
        EventModel.date > datetime.now()
    ).offset(skip).limit(limit).all()
    return events 

@router.get("/events/{event_id}", response_model=Event)
async def get_event_details(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event