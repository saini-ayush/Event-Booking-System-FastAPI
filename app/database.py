from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Database connected")

Base = declarative_base()

from .models.user import User
from .models.event import Event
from .models.booking import Booking

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()