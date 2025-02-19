from fastapi import APIRouter
from .endpoints import auth, events, booking

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    events.router,
    tags=["events"]
)

api_router.include_router(
    booking.router,
    tags=["bookings"]
)