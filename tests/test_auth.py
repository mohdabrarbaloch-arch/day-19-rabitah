"""Tests: authentication.""""


def test_register_returns_token(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "a@b.com", "username": "alice", "password": "secret123"},
    )
    assert res.status_code == 201
    body = res.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_register_rejects_weak_password(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "a@b.com", "username": "alice", "password": "secretonly"},
    )
    assert res.status_code == 422


def test_register_rejects_bad_username(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "a@b.com", "username": "ALICE BAD!", "password": "secret123"},
    )
    assert res.status_code == 422


def test_register_duplicate_email_conflict(client):
    payload = {"email": "dup@b.com", "username": "bob", "password": "secret123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    res = client.post(
        "/api/auth/register",
        json={"email": "dup@b.com", "username": "bob2", "password": "secret123"},
    )
    assert res.status_code == 409


def test_register_duplicate_username_conflict(client):
    payload = {"email": "x@b.com", "username": "carol", "password": "secret123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    res = client.post(
        "/api/auth/register",
        json={"email": "x2@b.com", "username": "carol", "password": "secret123"},
    )
    assert res.status_code == 409


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "l@b.com", "username": "loginuser", "password": "secret123"},
    )
    res = client.post(
        "/api/auth/login", json={"email": "l@b.com", "password": "secret123"}
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "w@b.com", "username": "wronguser", "password": "secret123"},
    )
    res = client.post(
        "/api/auth/login", json={"email": "w@b.com", "password": "nope1234"}
    )
    assert res.status_code == 401


def test_me_requires_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_returns_profile(client):
    token = client.post(
        "/api/auth/register",
        json={"email": "m@b.com", "username": "meuser", "password": "secret123"},
    ).json()["access_token"]
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "meuser"


def test_update_profile_theme(client):
    token = client.post(
        "/api/auth/register",
        json={"email": "t@b.com", "username": "themeuser", "password": "secret123"},
    ).json()["access_token"].replace("", "")
    token = client.post(
        "/api/auth/register",
        json={"email": "t@b.com", "username": "themeuser", "password": "secret123"},
    ).json()["access_token"]
    res = client.patch(
        "/api/auth/me",
        json={"theme": "sunset"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["theme"] == "sunset"


def test_update_profile_invalid_theme(client):
    token = client.post(
        "/api/auth/register",
        json={"email": "i@b.com", "username": "badtheme", "password": "secret123"},
    ).json()["access_token"]
    res = client.patch(
        "/api/auth/me",
        json={"theme": "neon"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422
