"""
Абстракции (порты), от которых зависят сервисы.

Сервисы работают только с этими протоколами (DIP), а конкретные
реализации лежат в app/infrastructure и подключаются в app/container.py.
Интерфейсы узкие (ISP): каждому потребителю — только нужные ему методы.
"""

from typing import Protocol

from app.domain.models import FarmProfile, ModelInfo, Prediction, RiskLevel


class RiskModel(Protocol):
    """
    Модель оценки риска.

    Контракт для любой реализации (LSP): predict() возвращает
    число в диапазоне [0; 1] и не изменяет входные данные.
    """

    info: ModelInfo

    def is_ready(self) -> bool: ...

    def predict(self, farm: FarmProfile) -> float: ...


class RiskClassifier(Protocol):
    def classify(self, score: float) -> RiskLevel: ...


class RecommendationPolicy(Protocol):
    def recommend(self, level: RiskLevel) -> str: ...


class BusinessRule(Protocol):
    def check(self, farm: FarmProfile) -> None:
        """Выбрасывает BusinessRuleViolation, если правило нарушено."""
        ...


class PredictionWriter(Protocol):
    def save(self, prediction: Prediction) -> None: ...


class PredictionReader(Protocol):
    def get(self, request_id: str) -> Prediction | None: ...

    def list_recent(self, limit: int, risk_level: RiskLevel | None = None) -> list[Prediction]:
        """Последние прогнозы, новые первыми."""
        ...
