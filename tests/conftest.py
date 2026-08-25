"""Test fixtures: isolated SQLite database + API client."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Isolated database BEFORE importing the app
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["SECRET_KEY"] = "test-secret-key-for-rabitah-tests"
os.environ["RATE_LIMIT_LOGIN"] = "1000/minute"
os.environ["RATE_LIMIT_REGISTER"] = "1000/minute"

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_db():
    """Wipe all tables before each test so fixtures start from a fresh DB."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    """Register + login a fresh user, return Authorization header."""
    res = client.post(
        "/api/auth/register",
        json={"email": "user@test.pk", "username": "testuser", "password": "pass12345"},
    )
    assert res.status_code == 201, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def second_user_headers(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "other@test.pk", "username": "otheruser", "password": "pass12345"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_link(client, auth_headers):
    res = client.post(
        "/api/links",
        json={"title": "My GitHub", "url": "https://github.com/test", "icon": "github"},
        headers=auth_headers,
    )
    assert res.status_code == 201, res.text
    return res.json()
