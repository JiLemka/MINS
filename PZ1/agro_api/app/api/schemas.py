"""
Pydantic-схемы — HTTP-контракт API.

Отвечают только за формат и структурную валидацию (ошибка -> 422)
и за преобразование между JSON и сущностями домена.
"""

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import FarmProfile, RiskLevel


class FarmRequest(BaseModel):
    """
    Данные сельскохозяйственного предприятия,
    которые клиент передает в POST /predict
    """

    farm_id: str = Field(..., min_length=1, description="Идентификатор хозяйства")
    region: str = Field(..., min_length=1, description="Регион хозяйства")
    crop_type: str = Field(..., min_length=1, description="Основная сельскохозяйственная культура")
    area_ha: float = Field(..., gt=0, description="Площадь посевов, га")
    temperature_avg: float = Field(..., ge=-60, le=60, description="Средняя температура, °C")
    precipitation_mm: float = Field(..., ge=0, description="Количество осадков, мм")
    payment_delay_days: int = Field(..., ge=0, description="Количество дней просрочки платежа")
    previous_defaults: int = Field(..., ge=0, description="Количество предыдущих дефолтов")
    debt: float = Field(..., ge=0, description="Текущая задолженность, руб.")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
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
            ]
        }
    )

    def to_domain(self) -> FarmProfile:
        return FarmProfile(**self.model_dump())


class PredictionResponse(BaseModel):
    """Структура ответа сервиса после выполнения прогноза."""

    model_config = ConfigDict(from_attributes=True)

    request_id: str
    farm_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    recommendation: str
    model_version: str


class HealthResponse(BaseModel):
    status: str


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    model_type: str
    status: str
