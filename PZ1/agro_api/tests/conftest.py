import pytest
from fastapi.testclient import TestClient

from app.domain.models import FarmProfile
from app.main import create_app

VALID_FARM = {
    "farm_id": "FARM-001",
    "region": "Krasnodar",
    "crop_type": "wheat",
    "area_ha": 2500,
    "temperature_avg": 24.3,
    "precipitation_mm": 320,
    "payment_delay_days": 45,
    "previous_defaults": 1,
    "debt": 6500000
}


@pytest.fixture
def client() -> TestClient:
    # Новое приложение на каждый тест — у каждого теста своё пустое хранилище
    return TestClient(create_app())


@pytest.fixture
def farm() -> FarmProfile:
    return FarmProfile(**VALID_FARM)
