from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    venue: str
    total_tickets: int
    price: float

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    venue: Optional[str] = None
    total_tickets: Optional[int] = None
    price: Optional[float] = None

class Event(EventBase):
    id: int
    available_tickets: int

    class Config:
        from_attributes = True
