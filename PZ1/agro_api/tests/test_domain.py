"""
Модульные тесты бизнес-логики — без HTTP и без FastAPI.

Возможны благодаря тому, что сервисы зависят от абстракций:
вместо настоящих модели и хранилища подставляются заглушки.
"""

from dataclasses import replace

import pytest

from app.domain.errors import BusinessRuleViolation, ModelUnavailableError, PredictionNotFoundError
from app.domain.models import ModelInfo, Prediction, RiskLevel
from app.infrastructure.business_rules import AllowedRegionRule
from app.infrastructure.in_memory_repository import InMemoryPredictionRepository
from app.infrastructure.postprocessing import MappingRecommendationPolicy, ThresholdRiskClassifier
from app.infrastructure.rule_based_model import RiskFactor, RuleBasedRiskModel
from app.services.prediction_service import PredictionService
from app.services.query_service import PredictionQueryService

INFO = ModelInfo(name="test-model", version="9.9", type="risk-scoring")


class FixedScoreModel:
    """Заглушка RiskModel: всегда возвращает заданный score."""

    def __init__(self, score: float, ready: bool = True) -> None:
        self.info = INFO
        self._score = score
        self._ready = ready

    def is_ready(self) -> bool:
        return self._ready

    def predict(self, farm) -> float:
        return self._score


def make_service(model, repository=None, rules=()):
    return PredictionService(
        model=model,
        classifier=ThresholdRiskClassifier(),
        recommendations=MappingRecommendationPolicy(),
        rules=list(rules),
        repository=repository or InMemoryPredictionRepository(),
        id_factory=lambda: "fixed-id"
    )


# --- Модель ---

def test_rule_based_model_example_from_task(farm):
    model = RuleBasedRiskModel(INFO)
    assert model.predict(farm) == 0.9


def test_rule_based_model_all_factors_capped_at_one(farm):
    risky = replace(farm, precipitation_mm=50)
    assert RuleBasedRiskModel(INFO).predict(risky) == 1.0


def test_rule_based_model_no_factors(farm):
    safe = replace(farm, payment_delay_days=0, previous_defaults=0, debt=0)
    assert RuleBasedRiskModel(INFO).predict(safe) == 0.1


def test_new_factor_added_without_changing_model(farm):
    frost = RiskFactor("frost", 0.2, lambda f: f.temperature_avg < 0)
    model = RuleBasedRiskModel(INFO, factors=[frost])
    assert model.predict(replace(farm, temperature_avg=-5)) == 0.3


# --- Постпроцессинг ---

@pytest.mark.parametrize("score, level", [
    (0.0, RiskLevel.LOW),
    (0.29, RiskLevel.LOW),
    (0.3, RiskLevel.MEDIUM),
    (0.69, RiskLevel.MEDIUM),
    (0.7, RiskLevel.HIGH),
    (1.0, RiskLevel.HIGH),
])
def test_classifier_thresholds(score, level):
    assert ThresholdRiskClassifier().classify(score) == level


def test_recommendations_cover_all_levels():
    policy = MappingRecommendationPolicy()
    assert all(policy.recommend(level) for level in RiskLevel)


# --- Бизнес-правила ---

def test_allowed_region_rule(farm):
    rule = AllowedRegionRule({"Krasnodar"})
    rule.check(farm)
    with pytest.raises(BusinessRuleViolation):
        rule.check(replace(farm, region="Moscow"))


# --- Сервисы ---

def test_service_uses_injected_model(farm):
    repository = InMemoryPredictionRepository()
    prediction = make_service(FixedScoreModel(0.5), repository).predict(farm)

    assert prediction == Prediction(
        request_id="fixed-id",
        farm_id="FARM-001",
        risk_score=0.5,
        risk_level=RiskLevel.MEDIUM,
        recommendation="Требуется дополнительная проверка",
        model_version="9.9"
    )
    assert repository.get("fixed-id") == prediction


def test_service_rejects_when_model_not_ready(farm):
    with pytest.raises(ModelUnavailableError):
        make_service(FixedScoreModel(0.5, ready=False)).predict(farm)


def test_service_checks_rules_before_saving(farm):
    repository = InMemoryPredictionRepository()
    service = make_service(FixedScoreModel(0.5), repository, rules=[AllowedRegionRule({"Rostov"})])

    with pytest.raises(BusinessRuleViolation):
        service.predict(farm)
    assert repository.list_recent(10) == []


def test_query_service_not_found():
    with pytest.raises(PredictionNotFoundError):
        PredictionQueryService(InMemoryPredictionRepository()).get("missing")
