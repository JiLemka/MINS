"""
Внедрение зависимостей в обработчики FastAPI.

Обработчики получают готовые сервисы через Depends и не создают их сами.
"""

from typing import Annotated

from fastapi import Depends, Request

from app.container import Container
from app.domain.ports import RiskModel
from app.services.prediction_service import PredictionService
from app.services.query_service import PredictionQueryService


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_model(container: Annotated[Container, Depends(get_container)]) -> RiskModel:
    return container.model


def get_prediction_service(container: Annotated[Container, Depends(get_container)]) -> PredictionService:
    return container.prediction_service


def get_query_service(container: Annotated[Container, Depends(get_container)]) -> PredictionQueryService:
    return container.query_service


ModelDep = Annotated[RiskModel, Depends(get_model)]
PredictionServiceDep = Annotated[PredictionService, Depends(get_prediction_service)]
QueryServiceDep = Annotated[PredictionQueryService, Depends(get_query_service)]
