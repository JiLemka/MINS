"""
Преобразование доменных ошибок в HTTP-ответы.

Формат тела совпадает с HTTPException FastAPI: {"detail": "..."}.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.errors import (
    BusinessRuleViolation,
    DomainError,
    ModelUnavailableError,
    PredictionNotFoundError
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    BusinessRuleViolation: status.HTTP_400_BAD_REQUEST,
    PredictionNotFoundError: status.HTTP_404_NOT_FOUND,
    ModelUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


async def domain_error_handler(request: Request, error: DomainError) -> JSONResponse:
    status_code = next(
        (code for error_type, code in STATUS_BY_ERROR.items() if isinstance(error, error_type)),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return JSONResponse(status_code=status_code, content={"detail": str(error)})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
