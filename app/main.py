from fastapi import FastAPI
from .api.v1.router import api_router
from .database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
]

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Booking System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def main():
    return {"msg": "Event management system"}
