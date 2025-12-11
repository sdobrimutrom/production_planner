from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.optimization import router as optimization_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Production Optimization Service",
        version="0.1.0",
        description=(
            "Сервис оптимизации производства на основе математической модели A "
            "(модель B будет добавлена позднее отдельной ручкой)."
        ),
    )

    app.include_router(optimization_router)

    @app.get("/", summary="Health check")
    def health_check() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
