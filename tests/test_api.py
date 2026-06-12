import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db

client = TestClient(app, raise_server_exceptions=False)

SAMPLE_NEWS = [
    {"id": "1", "title": "Сбербанк показал рекордную прибыль", "text": "", "company": "Сбербанк", "location": "Москва", "industry": "Финансы"},
    {"id": "2", "title": "Лукойл получил штраф за нарушение", "text": "", "company": "Лукойл", "location": "СПб", "industry": "Нефть"},
]


def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_cluster_valid_input():
    r = client.post("/cluster", json=SAMPLE_NEWS)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert all("ids" in c and "count" in c for c in data)


def test_cluster_empty_list_returns_400():
    r = client.post("/cluster", json=[])
    assert r.status_code == 400


def test_cluster_blank_id_returns_422():
    r = client.post("/cluster", json=[{"id": "", "title": "test", "text": ""}])
    assert r.status_code == 422


def test_cluster_blank_title_returns_422():
    r = client.post("/cluster", json=[{"id": "1", "title": "   ", "text": ""}])
    assert r.status_code == 422


def test_sentiment_valid_input():
    r = client.post("/sentiment", json=SAMPLE_NEWS)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    scores = [item["score"] for item in data]
    assert scores == sorted(scores)


def test_sentiment_empty_list_returns_400():
    r = client.post("/sentiment", json=[])
    assert r.status_code == 400


def test_sentiment_blank_id_returns_422():
    r = client.post("/sentiment", json=[{"id": "  ", "title": "test", "text": ""}])
    assert r.status_code == 422


def test_analyze_db_unavailable_returns_503():
    def mock_db_operational_error():
        mock = MagicMock()
        mock.merge.side_effect = OperationalError("conn", None, None)
        yield mock

    app.dependency_overrides[get_db] = mock_db_operational_error
    try:
        r = client.post("/analyze", json=SAMPLE_NEWS)
        assert r.status_code == 503
        assert "Database unavailable" in r.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_analyze_db_error_returns_500():
    def mock_db_sql_error():
        mock = MagicMock()
        mock.merge.side_effect = SQLAlchemyError("unexpected")
        yield mock

    app.dependency_overrides[get_db] = mock_db_sql_error
    try:
        r = client.post("/analyze", json=SAMPLE_NEWS)
        assert r.status_code == 500
    finally:
        app.dependency_overrides.clear()


def test_analyze_empty_list_returns_400():
    r = client.post("/analyze", json=[])
    assert r.status_code == 400


def test_news_db_unavailable_returns_503():
    def mock_db_operational_error():
        mock = MagicMock()
        mock.query.side_effect = OperationalError("conn", None, None)
        yield mock

    app.dependency_overrides[get_db] = mock_db_operational_error
    try:
        r = client.get("/news")
        assert r.status_code == 503
    finally:
        app.dependency_overrides.clear()
