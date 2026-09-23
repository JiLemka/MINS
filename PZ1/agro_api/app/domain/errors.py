"""
Ошибки предметной области.

Домен не знает про HTTP-коды: их сопоставление с ошибками
выполняет API-слой (app/api/error_handlers.py).
"""


class DomainError(Exception):
    """Базовая ошибка предметной области."""


class BusinessRuleViolation(DomainError):
    """Данные корректны по формату, но нарушают бизнес-правило."""


class ModelUnavailableError(DomainError):
    def __init__(self) -> None:
        super().__init__("Model is temporarily unavailable")


class PredictionNotFoundError(DomainError):
    def __init__(self, request_id: str) -> None:
        self.request_id = request_id
        super().__init__("Prediction not found")
