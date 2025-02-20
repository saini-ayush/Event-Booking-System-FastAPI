#app/tests/test_bookings.py
from datetime import datetime, timedelta
import pytest
from .test_events import create_test_admin, get_admin_token

def create_test_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "user123",
            "is_admin": False
        }
    )
    assert response.status_code == 201
    return response.json()

def get_user_token(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "user@example.com",
            "password": "user123"
        }
    )
    return response.json()["access_token"]

def create_test_event(client, admin_token):
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "date": (datetime.now() + timedelta(days=1)).isoformat(),
        "venue": "Test Venue",
        "total_tickets": 100,
        "price": 900
    }
    
    response = client.post(
        "/api/v1/admin/events",
        json=event_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    return response.json()

@pytest.mark.parametrize("number_of_tickets, expected_status", [
    (2, 201),
    (5, 201),
])
def test_book_event(client, number_of_tickets, expected_status):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    event = create_test_event(client, admin_token)

    create_test_user(client)
    user_token = get_user_token(client)

    booking_data = {
        "number_of_tickets": number_of_tickets,
        "event_id": event['id']
    }

    response = client.post(
        f"/api/v1/events/{event['id']}/book",
        json=booking_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == expected_status
    data = response.json()
    assert data["number_of_tickets"] == number_of_tickets
    assert data["event_id"] == event["id"]

@pytest.mark.parametrize("number_of_tickets, expected_status", [
    (2, 200),
    (5, 200),
])
def test_cancel_booking(client, number_of_tickets, expected_status):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    event = create_test_event(client, admin_token)

    create_test_user(client)
    user_token = get_user_token(client)

    booking_data = {
        "number_of_tickets": number_of_tickets,
        "event_id": event['id']
    }

    book_response = client.post(
        f"/api/v1/events/{event['id']}/book",
        json=booking_data,
        headers={"Authorization": f"Bearer {user_token}"}
    )

    cancel_response = client.delete(
        f"/api/v1/events/{event['id']}/cancel",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert cancel_response.status_code == expected_status

    event_response = client.get(f"/api/v1/events/{event['id']}")
    updated_event = event_response.json()
    assert updated_event["available_tickets"] == event["total_tickets"]
