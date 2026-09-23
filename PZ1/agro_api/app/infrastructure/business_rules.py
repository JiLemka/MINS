"""
Бизнес-правила: проверки, которые нельзя выразить типом значения.

Новое правило — новый класс с методом check(), добавленный
в список правил в app/container.py (OCP).
"""

from collections.abc import Iterable

from app.domain.errors import BusinessRuleViolation
from app.domain.models import FarmProfile


class AllowedRegionRule:
    """Реализует протокол BusinessRule: регион должен быть в справочнике."""

    def __init__(self, allowed_regions: Iterable[str]) -> None:
        self._allowed_regions = frozenset(allowed_regions)

    def check(self, farm: FarmProfile) -> None:
        if farm.region not in self._allowed_regions:
            raise BusinessRuleViolation(
                f"Unknown region: {farm.region}. "
                f"Allowed regions: {sorted(self._allowed_regions)}"
            )
