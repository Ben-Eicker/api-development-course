from .. import schemas


def test_create_user(client):
    response = client.post(
        "/users/",
        json={"email": "max.mustermann@gmail.com", "password": "musterpassword"},
    )
    assert response.status_code == 201
    new_user = schemas.UserResponse(**response.json())
    assert new_user.user_id == 1
    assert new_user.email == "max.mustermann@gmail.com"


def test_create_user_duplicate_email(client, test_user):
    response = client.post(
        "/users/",
        json={"email": test_user["email"], "password": "anotherpassword"},
    )
    assert response.status_code == 409


def test_get_user(client, test_user):
    response = client.get(f"/users/{test_user['user_id']}")
    assert response.status_code == 200
    fetched_user = schemas.UserResponse(**response.json())
    assert fetched_user.user_id == test_user["user_id"]
    assert fetched_user.email == test_user["email"]


def test_get_user_not_found(client):
    response = client.get("/users/88888")
    assert response.status_code == 404
