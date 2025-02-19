from pydantic import BaseModel
from datetime import datetime

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