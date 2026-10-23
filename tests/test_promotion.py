import pytest

from scripts import promote

IMAGE = "ghcr.io/example/app@sha256:" + "a" * 64
DATABASE = "ghcr.io/example/db@sha256:" + "b" * 64


def test_stale_source_cannot_promote(monkeypatch):
    monkeypatch.setenv("SOURCE_SHA", "old-source")
    monkeypatch.setenv("RELEASE_IMAGE", IMAGE)
    monkeypatch.setenv("DATABASE_IMAGE", DATABASE)
    calls = []

    def fake_api(path, payload=None, method=None):
        calls.append(path)
        assert payload is None
        return {"object": {"sha": "new-main"}}

    monkeypatch.setattr(promote, "api", fake_api)
    with pytest.raises(RuntimeError, match="stale"):
        promote.main()
    assert calls == ["git/ref/heads/main"]


def test_mutable_image_cannot_promote(monkeypatch):
    monkeypatch.setenv("SOURCE_SHA", "source")
    monkeypatch.setenv("RELEASE_IMAGE", "ghcr.io/example/app:latest")
    monkeypatch.setenv("DATABASE_IMAGE", DATABASE)
    monkeypatch.setattr(promote, "api", lambda *_: pytest.fail("API must not be called"))
    with pytest.raises(ValueError, match="digest"):
        promote.main()
