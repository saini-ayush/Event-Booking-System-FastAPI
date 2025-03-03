from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import User
from app.schemas.event import Event


class BookingBase(BaseModel):
    number_of_tickets: int


class BookingCreate(BookingBase):
    event_id: int


class Booking(BookingBase):
    id: int
    user_id: int
    event_id: int
    booking_date: datetime

    class Config:
        from_attributes = True


class BookingWithDetails(BaseModel):
    id: int
    event_id: int
    user_id: int
    user_email: str
    num_tickets: int  # This corresponds to number_of_tickets in your DB
    total_price: float  # This will be calculated
    booking_date: datetime
    event: Event

    class Config:
        from_attributes = True
