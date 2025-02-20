# FastAPI Event management

A FastAPI-based REST API for managing events and bookings with role-based access control.

## Features

- User Authentication with JWT
- Role-based Access Control (Admin/User)
- Event Management
- Booking System
- PostgreSQL Database Integration

## Tech Stack

- Python 3.8+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT Authentication

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/saini-ayush/Event-Booking-System-FastAPI.git
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/event_booking_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Create the database:
```sql
CREATE DATABASE event_booking_db;
```

## Running the Application

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get access token

### Admin Endpoints
- `POST /api/v1/admin/events` - Create event
- `PUT /api/v1/admin/events/{id}` - Update event
- `DELETE /api/v1/admin/events/{id}` - Delete event
- `GET /api/v1/admin/events` - View all events
- `GET /api/v1/admin/bookings` - View all bookings

### User Endpoints
- `GET /api/v1/events` - View available events
- `POST /api/v1/events/{id}/book` - Book tickets
- `DELETE /api/v1/events/{id}/cancel` - Cancel booking
- `GET /api/v1/events/history` - View booking history

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Project Structure 

```
└── 📁FastAPIEventManagement
    └── 📁app
        └── 📁api
            └── __init__.py
            └── 📁v1
                └── __init__.py
                └── 📁endpoints
                    └── 📁__pycache__
                    └── auth.py
                    └── booking.py
                    └── events.py
                └── router.py
        └── config.py
        └── 📁core
            └── __init__.py
            └── security.py
        └── database.py
        └── dependencies.py
        └── main.py
        └── 📁models
            └── __init__.py
            └── booking.py
            └── event.py
            └── user.py
        └── 📁schemas
            └── __init__.py
            └── booking.py
            └── event.py
            └── user.py
    └── .env
    └── .gitignore
    └── README.md
    └── requirements.txt
```