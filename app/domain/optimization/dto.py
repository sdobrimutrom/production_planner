from typing import List, Dict, Optional, Union
from datetime import date
from pydantic import BaseModel

from app.schemas.optimization import OptimizationParamsIn, OptimizationParamsInB
# -------------------------------------------------------------
# Внешние DTO — приходят из API
# -------------------------------------------------------------

class OrderData(BaseModel):
    order_id: int
    product_id: int
    production_type: str  # "serial" / "non_serial"
    quantity: float
    deadline: date


class ProductData(BaseModel):
    product_id: int


class TeamData(BaseModel):
    team_id: int


class TeamProductivityData(BaseModel):
    team_id: int
    product_id: int
    serial_rate: float
    non_serial_rate: float


class OptimizationParams(BaseModel):
    k_tardy_default: float = 10_000.0
    delta_buffer: float = 0.17     # распределение риска на месяц
    alpha: float = 0.5
    beta: float = 0.5


class OptimizationInput(BaseModel):
    start_date: date
    num_days: int

    orders: List[OrderData]
    teams: List[TeamData]
    products: List[ProductData]

    productivity: Dict[tuple, TeamProductivityData]

    params: OptimizationParams


# -------------------------------------------------------------
# ВНУТРЕННИЕ DTO — подготовленный формат solver’а
# -------------------------------------------------------------

class PreparedOrder(BaseModel):
    index: int
    order_id: int
    product_id: int
    production_type: str
    quantity: float
    deadline: int  # дедлайн в днях (число от 0 до num_days)


class PreparedTeamProductivity(BaseModel):
    team_id: int
    product_id: int
    serial_rate: float
    non_serial_rate: float


class PreparedInput(BaseModel):
    orders: List[PreparedOrder]
    teams: List[TeamData]
    products: List[ProductData]
    productivity: List[PreparedTeamProductivity]

    start_date: date
    num_days: int

    t_ojd: Dict[tuple, float]
    H_jd: Dict[tuple, float]
    params: Union[OptimizationParamsIn, OptimizationParamsInB]

    day_list: List[date]

class DayTask(BaseModel):
    day_index: int
    work_date: date
    product_id: int
    production_type: str
    planned_hours: float
    planned_quantity: float


class TeamDayPlan(BaseModel):
    team_id: int
    day_index: int
    work_date: date
    tasks: List[DayTask]


class OptimizationResult(BaseModel):
    objective_value: float
    team_day_plans: List[TeamDayPlan]
    order_tardiness: Dict[int, float]
