"""Tests: authentication."""


def test_register_returns_token(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "new@test.pk", "username": "newuser", "password": "secret123"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_register_duplicate_email_conflict(client):
    client.post(
        "/api/auth/register",
        json={"email": "dup@test.pk", "username": "dupuser", "password": "secret123"},
    )
    res = client.post(
        "/api/auth/register",
        json={"email": "dup@test.pk", "username": "another", "password": "secret123"},
    )
    assert res.status_code == 409


def test_register_duplicate_username_conflict(client):
    client.post(
        "/api/auth/register",
        json={"email": "u1@test.pk", "username": "sameuser", "password": "secret123"},
    )
    res = client.post(
        "/api/auth/register",
        json={"email": "u2@test.pk", "username": "sameuser", "password": "secret123"},
    )
    assert res.status_code == 409


def test_register_rejects_bad_username(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "bad@test.pk", "username": "Bad User!", "password": "secret123"},
    )
    assert res.status_code == 422


def test_register_rejects_weak_password(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "weak@test.pk", "username": "weakuser", "password": "abcdefgh"},
    )
    assert res.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@test.pk", "username": "loginuser", "password": "secret123"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "login@test.pk", "password": "secret123"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "wrong@test.pk", "username": "wronguser", "password": "secret123"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "wrong@test.pk", "password": "not-the-password"},
    )
    assert res.status_code == 401


def test_me_requires_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_returns_profile(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"


def test_update_profile_theme(client, auth_headers):
    res = client.patch(
        "/api/auth/me",
        json={"display_name": "Test Person", "theme": "sunset"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["display_name"] == "Test Person"
    assert body["theme"] == "sunset"


def test_update_profile_invalid_theme(client, auth_headers):
    res = client.patch("/api/auth/me", json={"theme": "neon-rainbow"}, headers=auth_headers)
    assert res.status_code == 422
