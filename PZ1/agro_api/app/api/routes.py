"""
HTTP-маршруты.

Обработчики «тонкие»: принимают запрос, вызывают сервис
и возвращают результат. Бизнес-логики здесь нет.
"""

from fastapi import APIRouter, Query, status

from app.api.dependencies import ModelDep, PredictionServiceDep, QueryServiceDep
from app.api.schemas import (
    FarmRequest,
    HealthResponse,
    ModelInfoResponse,
    PredictionResponse
)
from app.domain.models import Prediction, RiskLevel

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["service"],
    summary="Проверка состояния сервиса",
    description="Возвращает текущее состояние API. Используется мониторингом и балансировщиком."
)
def health():
    return HealthResponse(status="ok")


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    tags=["service"],
    summary="Информация о модели",
    description="Возвращает название, версию, тип и текущее состояние модели."
)
def model_info(model: ModelDep):
    return ModelInfoResponse(
        model_name=model.info.name,
        model_version=model.info.version,
        model_type=model.info.type,
        status="ready" if model.is_ready() else "unavailable"
    )


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["predictions"],
    summary="Оценка риска хозяйства",
    description=(
        "Выполняет инференс модели агроскоринга: принимает характеристики "
        "хозяйства, проверяет бизнес-правила, рассчитывает риск и сохраняет результат."
    ),
    responses={
        400: {"description": "Нарушено бизнес-правило (неизвестный регион)"},
        503: {"description": "Модель временно недоступна"}
    }
)
def predict(request: FarmRequest, service: PredictionServiceDep) -> Prediction:
    return service.predict(request.to_domain())


@router.get(
    "/predictions",
    response_model=list[PredictionResponse],
    tags=["predictions"],
    summary="Список прогнозов",
    description=(
        "Возвращает последние выполненные прогнозы (новые первыми). "
        "Поддерживает ограничение количества и фильтрацию по уровню риска."
    )
)
def get_predictions(
    service: QueryServiceDep,
    limit: int = Query(default=10, ge=1, le=100, description="Максимальное количество результатов"),
    risk_level: RiskLevel | None = Query(default=None, description="Фильтр по категории риска")
) -> list[Prediction]:
    return service.list_recent(limit, risk_level)


@router.get(
    "/predictions/{request_id}",
    response_model=PredictionResponse,
    tags=["predictions"],
    summary="Получение прогноза по ID",
    description="Возвращает сохраненный прогноз по его уникальному идентификатору.",
    responses={404: {"description": "Прогноз не найден"}}
)
def get_prediction(request_id: str, service: QueryServiceDep) -> Prediction:
    return service.get(request_id)
