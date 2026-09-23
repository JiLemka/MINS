"""
Тестирование API через HTTP (Задание 10).

Запуск: pytest -v
"""

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from tests.conftest import VALID_FARM

LOW_RISK_FARM = {**VALID_FARM, "farm_id": "FARM-002", "payment_delay_days": 0,
                 "previous_defaults": 0, "debt": 100000}


# 1
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# 2
def test_model_info(client):
    response = client.get("/model-info")
    assert response.status_code == 200
    assert response.json() == {
        "model_name": "agro-risk-model",
        "model_version": "1.0",
        "model_type": "risk-scoring",
        "status": "ready"
    }


# 3
def test_predict_valid(client):
    response = client.post("/predict", json=VALID_FARM)
    assert response.status_code == 200
    body = response.json()
    assert body["farm_id"] == "FARM-001"
    assert body["risk_score"] == 0.9
    assert body["risk_level"] == "high"
    assert body["recommendation"] == "Высокий риск. Требуется ручное рассмотрение"
    assert body["model_version"] == "1.0"


# 4
def test_predict_negative_area(client):
    response = client.post("/predict", json={**VALID_FARM, "area_ha": -100})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "area_ha"]


# 5
def test_predict_unknown_region(client):
    response = client.post("/predict", json={**VALID_FARM, "region": "Moscow"})
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unknown region: Moscow. Allowed regions: ['Krasnodar', 'Rostov', 'Stavropol']"
    }


# 6
def test_get_existing_prediction(client):
    created = client.post("/predict", json=VALID_FARM).json()
    response = client.get(f"/predictions/{created['request_id']}")
    assert response.status_code == 200
    assert response.json() == created


# 7
def test_get_unknown_prediction(client):
    response = client.get("/predictions/unknown-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Prediction not found"}


# 8
def test_list_limit(client):
    for _ in range(3):
        client.post("/predict", json=VALID_FARM)
    response = client.get("/predictions", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2


# 9
def test_list_filter_high(client):
    client.post("/predict", json=LOW_RISK_FARM)
    high_id = client.post("/predict", json=VALID_FARM).json()["request_id"]
    response = client.get("/predictions", params={"risk_level": "high"})
    assert response.status_code == 200
    assert [item["request_id"] for item in response.json()] == [high_id]


# 10
def test_list_negative_limit(client):
    response = client.get("/predictions", params={"limit": -5})
    assert response.status_code == 422


# Дополнительно

def test_list_newest_first(client):
    first = client.post("/predict", json=VALID_FARM).json()["request_id"]
    second = client.post("/predict", json=LOW_RISK_FARM).json()["request_id"]
    ids = [item["request_id"] for item in client.get("/predictions").json()]
    assert ids == [second, first]


def test_list_invalid_risk_level(client):
    response = client.get("/predictions", params={"risk_level": "extreme"})
    assert response.status_code == 422


def test_predict_missing_field(client):
    body = {key: value for key, value in VALID_FARM.items() if key != "debt"}
    response = client.post("/predict", json=body)
    assert response.status_code == 422


def test_model_unavailable():
    # Зависимости задаются конфигурацией, без подмены глобальных переменных
    client = TestClient(create_app(Settings(model_ready=False)))

    assert client.get("/model-info").json()["status"] == "unavailable"

    response = client.post("/predict", json=VALID_FARM)
    assert response.status_code == 503
    assert response.json() == {"detail": "Model is temporarily unavailable"}


def test_process_time_header(client):
    assert "x-process-time" in client.get("/health").headers
