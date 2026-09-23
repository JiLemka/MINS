"""
Точка входа приложения.

Запуск: uvicorn app.main:app --reload
"""

import logging

from fastapi import FastAPI

from app.api.error_handlers import register_error_handlers
from app.api.middleware import add_process_time
from app.api.routes import router
from app.config import Settings
from app.container import Container, build_container


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    settings = settings or Settings()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version
    )
    app.state.container = container or build_container(settings)

    app.middleware("http")(add_process_time)
    register_error_handlers(app)
    app.include_router(router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
