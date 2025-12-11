from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ProductionTypeEnum(str, Enum):
    serial = "serial"
    non_serial = "non_serial"


class OrderIn(BaseModel):
    order_id: int = Field(..., description="Уникальный идентификатор заказа в БД основного сервиса")
    product_id: int = Field(..., description="ID изделия")
    production_type: ProductionTypeEnum = Field(..., description="Тип производства: serial / non_serial")
    quantity: float = Field(..., gt=0, description="Требуемое количество изделий по заказу")
    deadline_date: date = Field(..., description="Календарная дата дедлайна в пределах сессии")


class TeamProductivityIn(BaseModel):
    team_id: int = Field(..., description="ID бригады")
    product_id: int = Field(..., description="ID изделия")
    production_type: ProductionTypeEnum = Field(..., description="Тип производства: serial / non_serial")
    productivity: float = Field(..., gt=0, description="Производительность, изделий в час")


class TeamDayAvailabilityIn(BaseModel):
    team_id: int
    work_date: date
    available_hours: float


class OptimizationParamsIn(BaseModel):
    k_tardy_default: float = Field(1.0, gt=0, description="Штраф за квадрат дня просрочки заказа")
    k_under: float = Field(1.0, gt=0, description="Штраф за квадрат часа недозагрузки")
    k_over: float = Field(1.0, gt=0, description="Штраф за квадрат часа переработки")
    delta_buffer: float = Field(
        0.17,
        ge=0,
        le=0.5,
        description="Доля консервативного буфера по человеко-часам (например, 0.17 для 17%)",
    )


class OptimizationRequestModelA(BaseModel):
    session_id: Optional[int] = Field(None, description="ID сессии в основной системе (для трассировки)")
    start_date: date = Field(..., description="Дата начала горизонта планирования")
    num_days: int = Field(30, gt=0, description="Горизонт планирования в днях")

    orders: List[OrderIn] = Field(..., description="Список заказов с остатками по объёму")
    team_productivity: List[TeamProductivityIn] = Field(
        ...,
        description=(
            "Производительность бригад по изделиям и типам производства "
            "(изделий в час при текущем фактическом составе бригад)."
        ),
    )

    params: OptimizationParamsIn = OptimizationParamsIn()


# ---------- Выходные схемы ----------


class DayTaskOut(BaseModel):
    day_index: int = Field(..., description="Номер дня относительно start_date, начиная с 1")
    work_date: date = Field(..., description="Календарная дата: start_date + (day_index-1)")
    product_id: int = Field(..., description="ID изделия")
    production_type: ProductionTypeEnum = Field(..., description="Тип производства")
    planned_hours: float = Field(..., description="Плановые часы работы бригады над этим изделием")
    planned_quantity: float = Field(..., description="Плановое количество изготовленных изделий")


class TeamDayPlanOut(BaseModel):
    team_id: int = Field(..., description="ID бригады")
    day_index: int = Field(..., description="Номер дня относительно start_date, начиная с 1")
    work_date: date = Field(..., description="Календарная дата")
    tasks: List[DayTaskOut] = Field(..., description="Набор заданий для бригады в этот день")


class OptimizationResponseModelA(BaseModel):
    objective_value: float = Field(..., description="Значение целевой функции после оптимизации")
    team_day_plans: List[TeamDayPlanOut] = Field(..., description="План по бригадам и дням")
    order_tardiness: Dict[int, float] = Field(
        ...,
        description="Карта: order_id -> T_o (опоздание в днях, >= 0)",
    )


class OptimizationParamsInB(OptimizationParamsIn):
    alpha: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Вес недогрузки (0..1). Обычно alpha + beta = 1."
    )
    beta: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Вес переработки (0..1). Обычно alpha + beta = 1."
    )

class OptimizationRequestModelB(BaseModel):
    session_id: Optional[int] = Field(None, description="ID сессии в основной системе (для трассировки)")
    start_date: date = Field(..., description="Дата начала горизонта планирования")
    num_days: int = Field(30, gt=0, description="Горизонт планирования в днях")

    orders: List[OrderIn] = Field(..., description="Список заказов с остатками по объёму")
    team_productivity: List[TeamProductivityIn] = Field(
        ...,
        description=(
            "Производительность бригад по изделиям и типам производства "
            "(изделий в час при текущем фактическом составе бригад)."
        ),
    )

    params: OptimizationParamsInB = OptimizationParamsInB()


# Ответ модели B по структуре такой же, как у модели A
OptimizationResponseModelB = OptimizationResponseModelA