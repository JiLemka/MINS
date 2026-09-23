"""
Сущности предметной области.

Не зависят ни от FastAPI, ни от Pydantic, ни от способа хранения:
это чистые данные, которыми обмениваются слои приложения.
"""

from dataclasses import dataclass
from enum import StrEnum


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class FarmProfile:
    """Сведения о сельскохозяйственном предприятии."""

    farm_id: str
    region: str
    crop_type: str
    area_ha: float
    temperature_avg: float
    precipitation_mm: float
    payment_delay_days: int
    previous_defaults: int
    debt: float


@dataclass(frozen=True)
class Prediction:
    """Результат оценки риска одного хозяйства."""

    request_id: str
    farm_id: str
    risk_score: float
    risk_level: RiskLevel
    recommendation: str
    model_version: str


@dataclass(frozen=True)
class ModelInfo:
    name: str
    version: str
    type: str
