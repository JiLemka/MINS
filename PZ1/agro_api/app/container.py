"""
Точка сборки (composition root).

Единственное место, где выбираются конкретные реализации абстракций.
Чтобы заменить модель или хранилище, достаточно изменить этот файл.
"""

from dataclasses import dataclass

from app.config import Settings
from app.domain.models import ModelInfo
from app.domain.ports import RiskModel
from app.infrastructure.business_rules import AllowedRegionRule
from app.infrastructure.in_memory_repository import InMemoryPredictionRepository
from app.infrastructure.postprocessing import MappingRecommendationPolicy, ThresholdRiskClassifier
from app.infrastructure.rule_based_model import RuleBasedRiskModel
from app.services.prediction_service import PredictionService
from app.services.query_service import PredictionQueryService


@dataclass(frozen=True)
class Container:
    model: RiskModel
    prediction_service: PredictionService
    query_service: PredictionQueryService


def build_container(settings: Settings) -> Container:
    model = RuleBasedRiskModel(
        info=ModelInfo(
            name=settings.model_name,
            version=settings.model_version,
            type=settings.model_type
        ),
        ready=settings.model_ready
    )
    repository = InMemoryPredictionRepository()

    return Container(
        model=model,
        prediction_service=PredictionService(
            model=model,
            classifier=ThresholdRiskClassifier(),
            recommendations=MappingRecommendationPolicy(),
            rules=[AllowedRegionRule(settings.allowed_regions)],
            repository=repository
        ),
        query_service=PredictionQueryService(repository)
    )
