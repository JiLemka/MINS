"""
Хранилище прогнозов в оперативной памяти.

Данные теряются при перезапуске. Для перехода на SQLite/PostgreSQL
достаточно написать другой класс с теми же методами и подключить
его в app/container.py — сервисы не изменятся (DIP).
"""

from itertools import islice

from app.domain.models import Prediction, RiskLevel


class InMemoryPredictionRepository:
    """Реализует протоколы PredictionWriter и PredictionReader."""

    def __init__(self) -> None:
        self._items: dict[str, Prediction] = {}

    def save(self, prediction: Prediction) -> None:
        self._items[prediction.request_id] = prediction

    def get(self, request_id: str) -> Prediction | None:
        return self._items.get(request_id)

    def list_recent(self, limit: int, risk_level: RiskLevel | None = None) -> list[Prediction]:
        newest_first = reversed(self._items.values())
        matching = (
            item for item in newest_first
            if risk_level is None or item.risk_level == risk_level
        )
        return list(islice(matching, limit))
