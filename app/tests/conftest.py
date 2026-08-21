import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .. import config, database, main, models, oauth2

SQLALCHEMY_DATABASE_URL = f"{config.settings.database_url}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)


@pytest.fixture
def session():
    database.Base.metadata.drop_all(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    main.app.dependency_overrides[database.get_db] = override_get_db
    return TestClient(main.app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "max.mustermann@gmail.com", "password": "musterpassword"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "erika.musterfrau@gmail.com", "password": "otherpassword"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_token(test_user):
    return oauth2.create_access_token({"sub": test_user["email"]})


@pytest.fixture
def authorized_client(client, test_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_token}",
    }
    return client


@pytest.fixture
def test_posts(test_user, session):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "user_id": test_user["user_id"],
        },
        {
            "title": "second title",
            "content": "second content",
            "user_id": test_user["user_id"],
        },
        {
            "title": "third title",
            "content": "third content",
            "user_id": test_user["user_id"],
        },
    ]

    session.add_all([models.Post(**post) for post in posts_data])
    session.commit()

    return session.query(models.Post).all()
