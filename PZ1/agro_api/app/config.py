from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    app_title: str = "Agro Scoring API"
    app_description: str = "REST API для оценки риска сельскохозяйственных предприятий."
    app_version: str = "1.0.0"

    model_name: str = "agro-risk-model"
    model_version: str = "1.0"
    model_type: str = "risk-scoring"
    # Если установить False, /predict будет возвращать HTTP 503
    model_ready: bool = True

    allowed_regions: frozenset[str] = field(
        default_factory=lambda: frozenset({"Krasnodar", "Rostov", "Stavropol"})
    )
