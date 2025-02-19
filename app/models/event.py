from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from ..database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    date = Column(DateTime)
    venue = Column(String)
    total_tickets = Column(Integer)
    available_tickets = Column(Integer)
    price = Column(Float)
    
    bookings = relationship("Booking", back_populates="event")
