"""
Сценарий «получить сохранённые прогнозы».

Отделён от PredictionService (SRP): чтение не зависит от модели
и получает от хранилища только интерфейс чтения (ISP).
"""

from app.domain.errors import PredictionNotFoundError
from app.domain.models import Prediction, RiskLevel
from app.domain.ports import PredictionReader


class PredictionQueryService:
    def __init__(self, repository: PredictionReader) -> None:
        self._repository = repository

    def get(self, request_id: str) -> Prediction:
        prediction = self._repository.get(request_id)

        if prediction is None:
            raise PredictionNotFoundError(request_id)

        return prediction

    def list_recent(self, limit: int, risk_level: RiskLevel | None = None) -> list[Prediction]:
        return self._repository.list_recent(limit, risk_level)
