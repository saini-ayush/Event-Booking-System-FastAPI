from datetime import datetime, timedelta
import pytest


def create_test_admin(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "admin123",
            "is_admin": True
        }
    )
    assert response.status_code == 201
    return response.json()

def get_admin_token(client):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]

@pytest.mark.parametrize("event_data, expected_status", [
    (
        {
            "title": "Test Event 1",
            "description": "Test Description 1",
            "date": (datetime.now() + timedelta(days=1)).isoformat(),
            "venue": "Test Venue 1",
            "total_tickets": 100,
            "price": 29.99
        },
        201
    ),
    (
        {
            "title": "Test Event 2",
            "description": "Test Description 2",
            "date": (datetime.now() + timedelta(days=2)).isoformat(),
            "venue": "Test Venue 2",
            "total_tickets": 200,
            "price": 49.99
        },
        201
    ),
])
def test_create_event(client, event_data, expected_status):
    create_test_admin(client)
    admin_token = get_admin_token(client)

    response = client.post(
        "/api/v1/admin/events",
        json=event_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == expected_status
    data = response.json()
    assert data["title"] == event_data["title"]
    assert data["available_tickets"] == event_data["total_tickets"]

@pytest.mark.parametrize("update_data, expected_status", [
    (
        {
            "title": "Updated Event 1",
            "price": 39.99
        },
        200
    ),
    (
        {
            "title": "Updated Event 2",
            "price": 59.99
        },
        200
    ),
])
def test_update_event(client, update_data, expected_status):
    create_test_admin(client)
    admin_token = get_admin_token(client)

    event_data = {
        "title": "Original Event",
        "description": "Original Description",
        "date": (datetime.now() + timedelta(days=1)).isoformat(),
        "venue": "Original Venue",
        "total_tickets": 100,
        "price": 29.99
    }

    create_response = client.post(
        "/api/v1/admin/events",
        json=event_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    event_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/admin/events/{event_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == expected_status
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["price"] == update_data["price"]
    assert data["description"] == event_data["description"]
