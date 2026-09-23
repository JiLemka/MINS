"""
Сценарий «оценить риск хозяйства» — контур инференса:
проверка модели -> бизнес-правила -> инференс -> постпроцессинг -> сохранение.
"""

import logging
import uuid
from collections.abc import Callable, Sequence

from app.domain.errors import ModelUnavailableError
from app.domain.models import FarmProfile, Prediction
from app.domain.ports import (
    BusinessRule,
    PredictionWriter,
    RecommendationPolicy,
    RiskClassifier,
    RiskModel
)

logger = logging.getLogger(__name__)


def _new_request_id() -> str:
    return str(uuid.uuid4())


class PredictionService:
    """
    Оркестрирует шаги инференса, но сам ни один из них не реализует:
    каждый шаг делегирован абстракции, переданной в конструктор.
    """

    def __init__(
        self,
        model: RiskModel,
        classifier: RiskClassifier,
        recommendations: RecommendationPolicy,
        rules: Sequence[BusinessRule],
        repository: PredictionWriter,
        id_factory: Callable[[], str] = _new_request_id
    ) -> None:
        self._model = model
        self._classifier = classifier
        self._recommendations = recommendations
        self._rules = rules
        self._repository = repository
        self._id_factory = id_factory

    def predict(self, farm: FarmProfile) -> Prediction:
        if not self._model.is_ready():
            raise ModelUnavailableError()

        for rule in self._rules:
            rule.check(farm)

        logger.info("Prediction request received | farm_id=%s", farm.farm_id)

        score = self._model.predict(farm)
        level = self._classifier.classify(score)

        prediction = Prediction(
            request_id=self._id_factory(),
            farm_id=farm.farm_id,
            risk_score=score,
            risk_level=level,
            recommendation=self._recommendations.recommend(level),
            model_version=self._model.info.version
        )

        self._repository.save(prediction)

        logger.info(
            "Prediction completed | request_id=%s | farm_id=%s | risk_score=%s | risk_level=%s | model_version=%s",
            prediction.request_id, farm.farm_id, score, level, prediction.model_version
        )

        return prediction
