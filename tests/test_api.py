from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_model():

    response = client.get(
        "/model"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "Ollama"


def test_search():

    response = client.get(
        "/search",
        params={
            "query": "machine learning",
            "top_k": 3
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "results" in data

    assert len(
        data["results"]
    ) <= 3