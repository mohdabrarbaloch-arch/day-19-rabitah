"""Tests: link management + ownership + click tracking + analytics."""


def _register(client, email, username):
    return client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": "secret123"},
    ).json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_links_require_auth(client):
    assert client.get("/api/links").status_code == 401
    assert client.post("/api/links", json={}).status_code == 401


def test_list_links_empty(client):
    token = _register(client, "l1@b.com", "listempty")
    res = client.get("/api/links", headers=_auth(token))
    assert res.status_code == 200
    assert res.json() == []


def test_create_link(client):
    token = _register(client, "c1@b.com", "createlink")
    res = client.post(
        "/api/links",
        json={"title": "GitHub", "url": "https://github.com", "icon": "github"},
        headers=_auth(token),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "GitHub"
    assert body["click_count"] == 0
    assert body["is_active"] is True


def test_create_link_rejects_bad_url(client):
    token = _register(client, "c2@b.com", "badurl")
    res = client.post(
        "/api/links",
        json={"title": "x", "url": "ftp://nope"},
        headers=_auth(token),
    )
    assert res.status_code == 422


def test_list_links_after_create(client):
    token = _register(client, "l2@b.com", "listfull")
    client.post(
        "/api/links",
        json={"title": "A", "url": "https://a.com"},
        headers=_auth(token),
    )
    res = client.get("/api/links", headers=_auth(token))
    assert len(res.json()) == 1


def test_update_link(client):
    token = _register(client, "u1@b.com", "updatelink")
    link_id = client.post(
        "/api/links",
        json={"title": "Old", "url": "https://old.com"},
        headers=_auth(token),
    ).json()["id"]
    res = client.patch(
        f"/api/links/{link_id}",
        json={"title": "New", "is_active": False},
        headers=_auth(token),
    )
    assert res.status_code == 200
    assert res.json()["title"] == "New"
    assert res.json()["is_active"] is False


def test_delete_link(client):
    token = _register(client, "d1@b.com", "deletelink")
    link_id = client.post(
        "/api/links",
        json={"title": "Gone", "url": "https://gone.com"},
        headers=_auth(token),
    ).json()["id"]
    res = client.delete(f"/api/links/{link_id}", headers=_auth(token))
    assert res.status_code == 204
    assert client.get("/api/links", headers=_auth(token)).json() == []


def test_cannot_touch_others_link(client):
    t1 = _register(client, "o1@b.com", "ownerone")
    t2 = _register(client, "o2@b.com", "ownertwo")
    link_id = client.post(
        "/api/links",
        json={"title": "Mine", "url": "https://mine.com"},
        headers=_auth(t1),
    ).json()["id"]
    assert client.patch(f"/api/links/{link_id}", json={"title": "x"}, headers=_auth(t2)).status_code == 404
    assert client.delete(f"/api/links/{link_id}", headers=_auth(t2)).status_code == 404


def test_go_redirects_and_counts(client):
    token = _register(client, "g1@b.com", "gocounter")
    link_id = client.post(
        "/api/links",
        json={"title": "Example", "url": "https://example.com"},
        headers=_auth(token),
    ).json()["id"]
    res = client.get(f"/go/{link_id}", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "https://example.com"
    links = client.get("/api/links", headers=_auth(token)).json()
    assert links[0]["click_count"] == 1


def test_go_missing_link_404(client):
    assert client.get("/go/99999", follow_redirects=False).status_code == 404


def test_go_inactive_link_404(client):
    token = _register(client, "g2@b.com", "goinactive")
    link_id = client.post(
        "/api/links",
        json={"title": "Off", "url": "https://off.com"},
        headers=_auth(token),
    ).json()["id"]
    client.patch(f"/api/links/{link_id}", json={"is_active": False}, headers=_auth(token))
    assert client.get(f"/go/{link_id}", follow_redirects=False).status_code == 404


def test_public_page(client):
    token = _register(client, "p1@b.com", "publicpage")
    client.post(
        "/api/links",
        json={"title": "GitHub", "url": "https://github.com"},
        headers=_auth(token),
    )
    res = client.get("/api/page/publicpage")
    assert res.status_code == 200
    body = res.json()
    assert body["username"] == "publicpage"
    assert len(body["links"]) == 1


def test_public_page_404(client):
    assert client.get("/api/page/nobody-here").status_code == 404


def test_public_page_hides_inactive(client):
    token = _register(client, "p2@b.com", "hideinactive")
    l1 = client.post(
        "/api/links",
        json={"title": "On", "url": "https://on.com"},
        headers=_auth(token),
    ).json()["id"]
    client.post(
        "/api/links",
        json={"title": "Off", "url": "https://off.com"},
        headers=_auth(token),
    )
    client.patch(f"/api/links/{l1}", json={"is_active": False}, headers=_auth(token))
    body = client.get("/api/page/hideinactive").json()
    assert all(link["is_active"] is not False for link in body["links"])
    assert len(body["links"]) == 1


def test_qr_endpoint_returns_png(client):
    token = _register(client, "q1@b.com", "qruser")
    link_id = client.post(
        "/api/links",
        json={"title": "QR", "url": "https://qr.com"},
        headers=_auth(token),
    ).json()["id"]
    res = client.get(f"/qr/{link_id}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert res.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_analytics_empty(client):
    token = _register(client, "a1@b.com", "analyticsempty")
    res = client.get("/api/analytics", headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert body["total_clicks"] == 0
    assert body["total_links"] == 0
    assert len(body["daily"]) == 14


def test_analytics_after_clicks(client):
    token = _register(client, "a2@b.com", "analyticsfull")
    link_id = client.post(
        "/api/links",
        json={"title": "Hit", "url": "https://hit.com"},
        headers=_auth(token),
    ).json()["id"]
    client.get(f"/go/{link_id}", follow_redirects=False)
    res = client.get("/api/analytics?days=7", headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert body["total_clicks"] == 1
    assert body["total_links"] == 1
    assert len(body["daily"]) == 7
    assert sum(d["count"] for d in body["daily"]) == 1


def test_analytics_requires_auth(client):
    assert client.get("/api/analytics").status_code == 401
