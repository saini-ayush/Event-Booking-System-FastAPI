from fastapi import FastAPI
from app.api.v1.router import api_router
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Booking System")

# Include all routes with version prefix
app.include_router(
    api_router,
    prefix="/api/v1"
)