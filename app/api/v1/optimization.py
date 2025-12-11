from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.optimization import (
    OptimizationRequestModelA,
    OptimizationRequestModelB,
    OptimizationResponseModelA,
    OptimizationResponseModelB,
)
from app.services.optimization_service import run_model_b, run_model_a

router = APIRouter(
    prefix="/api/v1/optimize",
    tags=["optimization"],
)


@router.post(
    "/model-a",
    response_model=OptimizationResponseModelA,
    summary="Запуск оптимизации (модель A)",
    description=(
        "Запуск базовой модели оптимизации (вариант A) "
        "с фиксированными штрафами за просрочку, недогрузку и переработку."
    ),
)
def optimize_model_a(payload: OptimizationRequestModelA) -> OptimizationResponseModelA:
    try:
        return run_model_a(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/model-b",
    response_model=OptimizationResponseModelB,
    summary="Запуск оптимизации (модель B с alpha/beta)",
    description=(
        "Запуск модели оптимизации (вариант B), в которой можно управлять относительной "
        "важностью недогрузки и переработки с помощью параметров alpha и beta. "
        "При alpha=0.2, beta=0.8 переработки существенно более нежелательны, "
        "при alpha=beta=0.5 недогрузка и переработка считаются одинаково нежелательными."
    ),
)
def optimize_model_b(payload: OptimizationRequestModelB) -> OptimizationResponseModelB:
    try:
        return run_model_b(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


