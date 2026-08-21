import pytest

from .. import schemas


def test_login(client, test_user):
    response = client.post(
        "/login/",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    token = schemas.Token(**response.json())
    assert token.token_type == "bearer"


@pytest.mark.parametrize(
    "email, password",
    [
        ("wrong@gmail.com", "musterpassword"),
        ("max.mustermann@gmail.com", "wrongpassword"),
        ("wrong@gmail.com", "wrongpassword"),
    ],
)
def test_login_invalid_credentials(client, test_user, email, password):
    response = client.post("/login/", data={"username": email, "password": password})
    assert response.status_code == 401
    assert response.json().get("detail") == "Invalid Credentials"
