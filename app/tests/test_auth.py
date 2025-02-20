import pytest

@pytest.mark.parametrize("email, password, is_admin, expected_status", [
    ("test1@example.com", "testpassword123", False, 201),
    ("test2@example.com", "anotherpassword", True, 201),
])
def test_register_user(client, email, password, is_admin, expected_status):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "is_admin": is_admin
        }
    )
    assert response.status_code == expected_status
    data = response.json()
    assert data["email"] == email
    assert "id" in data
    assert "is_admin" in data

@pytest.mark.parametrize("email, password, expected_status, expected_detail", [
    ("test1@example.com", "testpassword123", 400, "Email already registered"),
    ("test2@example.com", "anotherpassword", 400, "Email already registered"),
])
def test_register_duplicate_user(client, email, password, expected_status, expected_detail):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "is_admin": False
        }
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "is_admin": False
        }
    )
    assert response.status_code == expected_status
    assert expected_detail in response.json()["detail"]

@pytest.mark.parametrize("email, password, expected_status", [
    ("test1@example.com", "testpassword123", 200),
    ("test2@example.com", "anotherpassword", 200),
])
def test_login_user(client, email, password, expected_status):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "is_admin": False
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    assert response.status_code == expected_status
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.parametrize("email, password, wrong_password, expected_status", [
    ("test1@example.com", "testpassword123", "wrongpassword", 401),
    ("test2@example.com", "anotherpassword", "wrongpassword", 401),
])
def test_login_wrong_password(client, email, password, wrong_password, expected_status):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "is_admin": False
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": wrong_password
        }
    )
    assert response.status_code == expected_status
