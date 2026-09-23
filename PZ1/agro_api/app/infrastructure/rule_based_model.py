"""
Модель оценки риска на правилах (заглушка вместо обученной ML-модели).

Каждый фактор риска — отдельный объект. Новый фактор добавляется
в список, а класс модели при этом не меняется (OCP).
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from app.domain.models import FarmProfile, ModelInfo


@dataclass(frozen=True)
class RiskFactor:
    """Условие, при выполнении которого score увеличивается на weight."""

    name: str
    weight: float
    applies: Callable[[FarmProfile], bool]


DEFAULT_RISK_FACTORS: tuple[RiskFactor, ...] = (
    RiskFactor("long_payment_delay", 0.3, lambda farm: farm.payment_delay_days > 30),
    RiskFactor("previous_defaults", 0.3, lambda farm: farm.previous_defaults > 0),
    RiskFactor("large_debt", 0.2, lambda farm: farm.debt > 5_000_000),
    # Малое количество осадков условно увеличивает аграрный риск
    RiskFactor("low_precipitation", 0.1, lambda farm: farm.precipitation_mm < 100),
)


class RuleBasedRiskModel:
    """Реализует протокол RiskModel."""

    def __init__(
        self,
        info: ModelInfo,
        factors: Sequence[RiskFactor] = DEFAULT_RISK_FACTORS,
        base_score: float = 0.1,
        ready: bool = True
    ) -> None:
        self.info = info
        self._factors = factors
        self._base_score = base_score
        self._ready = ready

    def is_ready(self) -> bool:
        return self._ready

    def predict(self, farm: FarmProfile) -> float:
        score = self._base_score + sum(
            factor.weight for factor in self._factors if factor.applies(farm)
        )

        # Контракт RiskModel: результат в диапазоне [0; 1]
        return round(min(max(score, 0.0), 1.0), 2)
