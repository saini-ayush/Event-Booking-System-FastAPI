from fastapi import FastAPI
from .api.v1.router import api_router
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Booking System")

app.include_router(
    api_router,
    prefix="/api/v1"
)

@app.get("/")
async def main():
    return {"msg": "Event management system"}


