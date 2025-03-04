from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from ....database import get_db
from ....models.booking import Booking as BookingModel
from ....models.event import Event as EventModel
from ....schemas.booking import Booking, BookingCreate, BookingWithDetails
from ....core.security import get_current_user, get_current_admin
from ....models.user import User
from datetime import datetime

router = APIRouter()


# Admin
@router.get(
    "/admin/booking",
    response_model=List[BookingWithDetails],
    dependencies=[Depends(get_current_admin)],
)
async def get_all_bookings(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
):
    bookings_data = (
        db.query(
            BookingModel.id,
            BookingModel.event_id,
            BookingModel.user_id,
            User.email.label("user_email"),
            BookingModel.number_of_tickets.label("num_tickets"),
            (BookingModel.number_of_tickets * EventModel.price).label("total_price"),
            BookingModel.booking_date,
            EventModel,
        )
        .join(User, BookingModel.user_id == User.id)
        .join(EventModel, BookingModel.event_id == EventModel.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for booking in bookings_data:
        result.append(
            {
                "id": booking.id,
                "event_id": booking.event_id,
                "user_id": booking.user_id,
                "user_email": booking.user_email,
                "num_tickets": booking.num_tickets,
                "total_price": booking.total_price,
                "booking_date": booking.booking_date,
                "event": booking[7],
            }
        )

    return result


@router.get(
    "/admin/events/{event_id}/booking",
    response_model=List[Booking],
    dependencies=[Depends(get_current_admin)],
)
async def get_event_bookings(event_id: int, db: Session = Depends(get_db)):
    bookings = db.query(BookingModel).filter(BookingModel.event_id == event_id).all()
    return bookings


# User
@router.post(
    "/events/{event_id}/book",
    response_model=Booking,
    status_code=status.HTTP_201_CREATED,
)
async def book_event(
    event_id: int,
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    if event.date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book tickets for past events",
        )

    if event.available_tickets < booking.number_of_tickets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough tickets available",
        )

    try:
        db_booking = BookingModel(
            user_id=current_user.id,
            event_id=event_id,
            number_of_tickets=booking.number_of_tickets,
        )

        event.available_tickets -= booking.number_of_tickets

        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)

        return db_booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating booking",
        )


@router.delete("/events/{event_id}/cancel")
async def cancel_booking(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = (
        db.query(BookingModel)
        .filter(
            and_(
                BookingModel.event_id == event_id,
                BookingModel.user_id == current_user.id,
            )
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    event = db.query(EventModel).filter(EventModel.id == event_id).first()

    if event.date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel bookings for past events",
        )

    try:
        event.available_tickets += booking.number_of_tickets

        db.delete(booking)
        db.commit()

        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling booking",
        )


@router.post("/events/history", response_model=List[BookingWithDetails])
async def get_booking_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    bookings_data = (
        db.query(
            BookingModel.id,
            BookingModel.event_id,
            BookingModel.user_id,
            User.email.label("user_email"),
            BookingModel.number_of_tickets.label("num_tickets"),
            (BookingModel.number_of_tickets * EventModel.price).label("total_price"),
            BookingModel.booking_date,
            EventModel,
        )
        .join(User, BookingModel.user_id == User.id)
        .join(EventModel, BookingModel.event_id == EventModel.id)
        .filter(BookingModel.user_id == current_user.id)
        .order_by(BookingModel.booking_date.desc())
        .all()
    )

    result = []
    for booking in bookings_data:
        result.append(
            {
                "id": booking.id,
                "event_id": booking.event_id,
                "user_id": booking.user_id,
                "user_email": booking.user_email,
                "num_tickets": booking.num_tickets,
                "total_price": booking.total_price,
                "booking_date": booking.booking_date,
                "event": booking[7],
            }
        )

    return result
