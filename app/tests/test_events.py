from datetime import datetime, timedelta
import pytest
from fastapi import status

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

def create_test_event(client, admin_token):
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "date": (datetime.now() + timedelta(days=1)).isoformat(),
        "venue": "Test Venue",
        "total_tickets": 100,
        "price": 29.99
    }
    response = client.post(
        "/api/v1/admin/events",
        json=event_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()

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
            "title": "Test Event" * 10,  # Long title
            "description": "Test Description" * 50,  # Long description
            "date": (datetime.now() + timedelta(days=365)).isoformat(),
            "venue": "Test Venue",
            "total_tickets": 10000,
            "price": 999.99
        },
        201
    )
])
def test_create_event_success(client, event_data, expected_status):
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
    assert "id" in data

def test_create_event_unauthorized(client):
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "date": (datetime.now() + timedelta(days=1)).isoformat(),
        "venue": "Test Venue",
        "total_tickets": 100,
        "price": 29.99
    }
    response = client.post("/api/v1/admin/events", json=event_data)
    assert response.status_code == 401

def test_create_event_invalid_date(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    
    event_data = {
        "title": "Test Event",
        "description": "Test Description",
        "date": (datetime.now() - timedelta(days=1)).isoformat(),  # Past date
        "venue": "Test Venue",
        "total_tickets": 100,
        "price": 29.99
    }
    
    response = client.post(
        "/api/v1/admin/events",
        json=event_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400

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
            "description": "Updated Description",
            "date": (datetime.now() + timedelta(days=5)).isoformat(),
            "venue": "Updated Venue",
            "total_tickets": 200,
            "price": 59.99
        },
        200
    )
])
def test_update_event_success(client, update_data, expected_status):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    event = create_test_event(client, admin_token)

    response = client.put(
        f"/api/v1/admin/events/{event['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == expected_status
    data = response.json()
    for key, value in update_data.items():
        assert data[key] == value

def test_update_nonexistent_event(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    
    update_data = {"title": "Updated Event"}
    response = client.put(
        "/api/v1/admin/events/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

def test_delete_event_success(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    event = create_test_event(client, admin_token)

    response = client.delete(
        f"/api/v1/admin/events/{event['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/events/{event['id']}")
    assert get_response.status_code == 404

def test_delete_nonexistent_event(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    
    response = client.delete(
        "/api/v1/admin/events/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

def test_get_all_events_admin(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    
    event1 = create_test_event(client, admin_token)
    event2 = create_test_event(client, admin_token)

    response = client.get(
        "/api/v1/admin/events",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(event["id"] == event1["id"] for event in data)
    assert any(event["id"] == event2["id"] for event in data)

def test_get_available_events(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    
    future_event = create_test_event(client, admin_token)
    
    past_event_data = {
        "title": "Past Event",
        "description": "Past Description",
        "date": (datetime.now() - timedelta(days=1)).isoformat(),
        "venue": "Past Venue",
        "total_tickets": 100,
        "price": 29.99
    }
    client.post(
        "/api/v1/admin/events",
        json=past_event_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    response = client.get("/api/v1/events")
    assert response.status_code == 200
    data = response.json()
    
    assert all(
        datetime.fromisoformat(event["date"]) > datetime.now()
        for event in data
    )

def test_get_event_details(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    event = create_test_event(client, admin_token)

    response = client.get(f"/api/v1/events/{event['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == event["id"]
    assert data["title"] == event["title"]
    assert data["description"] == event["description"]

def test_get_nonexistent_event_details(client):
    response = client.get("/api/v1/events/99999")
    assert response.status_code == 404

# Test pagination
def test_events_pagination(client):
    create_test_admin(client)
    admin_token = get_admin_token(client)
    
    # Create multiple events
    for _ in range(5):
        create_test_event(client, admin_token)

    # Test with different skip/limit combinations
    response1 = client.get("/api/v1/events?skip=0&limit=2")
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1) == 2

    response2 = client.get("/api/v1/events?skip=2&limit=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2) == 2
    
    # Ensure different pages return different events
    assert data1[0]["id"] != data2[0]["id"]