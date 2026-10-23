import psycopg
import pytest

import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app, "query_releases", lambda: [{"version": "0.1.0", "description": "Demo"}]
    )
    return app.create_app().test_client()


def test_inventory_and_headers(client):
    response = client.get("/api/releases")
    assert response.status_code == 200
    assert response.json["releases"][0]["version"] == "0.1.0"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_database_failure_affects_readiness_not_liveness(client, monkeypatch):
    def unavailable():
        raise psycopg.OperationalError("private database details")

    monkeypatch.setattr(app, "query_releases", unavailable)
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 503
    response = client.get("/api/releases")
    assert response.status_code == 503
    assert b"private database details" not in response.data


def test_write_requests_rejected(client):
    assert client.post("/api/releases", json={"version": "injected"}).status_code == 405


def test_logs_do_not_include_query_string(client, caplog):
    with caplog.at_level("INFO"):
        client.get("/missing?token=never-log-this")
    assert "never-log-this" not in caplog.text
    assert '"route": "unmatched"' in caplog.text


def test_request_id_is_server_generated(client):
    response = client.get("/", headers={"X-Request-ID": "untrusted"})
    assert response.headers["X-Request-ID"] != "untrusted"
