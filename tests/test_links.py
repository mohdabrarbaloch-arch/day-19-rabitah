"""Tests: link management + ownership + click tracking + analytics."""


def test_create_link(client, auth_headers):
    res = client.post(
        "/api/links",
        json={"title": "My GitHub", "url": "https://github.com/test", "icon": "github"},
        headers=auth_headers,
    )
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "My GitHub"
    assert body["click_count"] == 0


def test_create_link_rejects_bad_url(client, auth_headers):
    res = client.post(
        "/api/links",
        json={"title": "Bad", "url": "not-a-url"},
        headers=auth_headers,
    )
    assert res.status_code == 422


def test_list_links_empty(client, auth_headers):
    res = client.get("/api/links", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_list_links_after_create(client, auth_headers, sample_link):
    res = client.get("/api/links", headers=auth_headers)
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == sample_link["id"]


def test_update_link(client, auth_headers, sample_link):
    res = client.patch(
        f"/api/links/{sample_link['id']}",
        json={"title": "Renamed", "is_active": False},
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "Renamed"
    assert body["is_active"] is False


def test_delete_link(client, auth_headers, sample_link):
    res = client.delete(f"/api/links/{sample_link['id']}", headers=auth_headers)
    assert res.status_code == 204
    res = client.get("/api/links", headers=auth_headers)
    assert res.json() == []


def test_cannot_touch_others_link(client, auth_headers, second_user_headers, sample_link):
    # second user cannot update
    res = client.patch(
        f"/api/links/{sample_link['id']}",
        json={"title": "Hacked"},
        headers=second_user_headers,
    )
    assert res.status_code == 404
    # second user cannot delete
    res = client.delete(f"/api/links/{sample_link['id']}", headers=second_user_headers)
    assert res.status_code == 404


def test_links_require_auth(client):
    assert client.get("/api/links").status_code == 401
    assert client.post("/api/links", json={}).status_code == 401


def test_go_redirects_and_counts(client, auth_headers, sample_link):
    res = client.get(f"/go/{sample_link['id']}", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "https://github.com/test"

    # count incremented
    links = client.get("/api/links", headers=auth_headers).json()
    assert links[0]["click_count"] == 1


def test_go_missing_link_404(client):
    assert client.get("/go/99999", follow_redirects=False).status_code == 404


def test_go_inactive_link_404(client, auth_headers, sample_link):
    client.patch(
        f"/api/links/{sample_link['id']}",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert client.get(f"/go/{sample_link['id']}", follow_redirects=False).status_code == 404


def test_qr_endpoint_returns_png(client, sample_link):
    res = client.get(f"/qr/{sample_link['id']}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert res.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_public_page(client, auth_headers, sample_link):
    res = client.get("/api/page/testuser")
    assert res.status_code == 200
    body = res.json()
    assert body["username"] == "testuser"
    assert len(body["links"]) == 1
    assert body["links"][0]["title"] == "My GitHub"


def test_public_page_hides_inactive(client, auth_headers, sample_link):
    client.patch(
        f"/api/links/{sample_link['id']}",
        json={"is_active": False},
        headers=auth_headers,
    )
    body = client.get("/api/page/testuser").json()
    assert body["links"] == []


def test_public_page_404(client):
    assert client.get("/api/page/nobody-here").status_code == 404


def test_analytics_empty(client, auth_headers):
    res = client.get("/api/analytics", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["total_clicks"] == 0
    assert body["total_links"] == 0
    assert len(body["daily"]) == 14


def test_analytics_after_clicks(client, auth_headers, sample_link):
    for _ in range(3):
        client.get(f"/go/{sample_link['id']}", follow_redirects=False)
    body = client.get("/api/analytics", headers=auth_headers).json()
    assert body["total_clicks"] == 3
    assert body["total_links"] == 1
    assert body["top_links"][0]["title"] == "My GitHub"
    assert body["daily"][-1]["count"] == 3


def test_analytics_requires_auth(client):
    assert client.get("/api/analytics").status_code == 401
