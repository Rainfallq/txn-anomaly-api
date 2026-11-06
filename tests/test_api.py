from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_baseline_endpoint():
    data = client.get("/baseline").json()
    assert data["n"] == 5000
    assert data["threshold"] == 3.0


def test_score_normal_amount():
    response = client.post("/score", json={"amount": 33.0})
    assert response.status_code == 200
    body = response.json()
    assert body["suspicious"] is False
    assert abs(body["z_score"]) < 3


def test_score_huge_amount_is_suspicious():
    body = client.post("/score", json={"amount": 5_000_000}).json()
    assert body["suspicious"] is True


def test_score_rejects_negative_amount():
    assert client.post("/score", json={"amount": -5}).status_code == 422


def test_score_rejects_missing_amount():
    assert client.post("/score", json={}).status_code == 422


def test_score_is_deterministic():
    first = client.post("/score", json={"amount": 100}).json()
    second = client.post("/score", json={"amount": 100}).json()
    assert first == second
