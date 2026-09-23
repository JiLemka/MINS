"""
Постпроцессинг: score -> категория риска -> рекомендация оператору.

Пороги и тексты передаются через конструктор, поэтому их можно
менять без правки кода классов (OCP).
"""

from collections.abc import Mapping

from app.domain.models import RiskLevel


class ThresholdRiskClassifier:
    """Реализует протокол RiskClassifier."""

    def __init__(self, medium_from: float = 0.3, high_from: float = 0.7) -> None:
        self._medium_from = medium_from
        self._high_from = high_from

    def classify(self, score: float) -> RiskLevel:
        if score < self._medium_from:
            return RiskLevel.LOW
        if score < self._high_from:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH


DEFAULT_RECOMMENDATIONS: Mapping[RiskLevel, str] = {
    RiskLevel.LOW: "Стандартное рассмотрение",
    RiskLevel.MEDIUM: "Требуется дополнительная проверка",
    RiskLevel.HIGH: "Высокий риск. Требуется ручное рассмотрение",
}


class MappingRecommendationPolicy:
    """Реализует протокол RecommendationPolicy."""

    def __init__(self, recommendations: Mapping[RiskLevel, str] = DEFAULT_RECOMMENDATIONS) -> None:
        self._recommendations = recommendations

    def recommend(self, level: RiskLevel) -> str:
        return self._recommendations[level]
