from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    booking_date = Column(DateTime, default=datetime.now)
    number_of_tickets = Column(Integer)
    
    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")