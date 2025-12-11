from __future__ import annotations

from datetime import timedelta
from typing import Dict, List, Tuple, Union

from app.schemas.optimization import (
    OptimizationRequestModelA,
    OptimizationRequestModelB,
    OptimizationResponseModelA,
    OptimizationResponseModelB,
)
from app.domain.optimization.dto import (
    PreparedInput,
    PreparedOrder,
    PreparedTeamProductivity,
    TeamData,
    ProductData,
    OptimizationResult,
)
from app.domain.optimization.model_a import solve_model_a
from app.domain.optimization.model_b import solve_model_b


# ---------- Буфер по месяцам (дельты) ----------

DELTA_BY_MONTH: Dict[int, float] = {
    1: 0.17,
    2: 0.16,
    3: 0.14,
    4: 0.13,
    5: 0.12,
    6: 0.11,
    7: 0.10,
    8: 0.10,
    9: 0.11,
    10: 0.13,
    11: 0.15,
    12: 0.17,
}

DEFAULT_DELTA: float = 0.15
BASE_HOURS_PER_DAY: float = 8.0


def build_optimization_input(
    data: Union[OptimizationRequestModelA, OptimizationRequestModelB]
) -> PreparedInput:

    start_date = data.start_date
    num_days = data.num_days

    # ---- 1. Команды и изделия ----
    team_ids = sorted({tp.team_id for tp in data.team_productivity})
    product_ids = sorted({o.product_id for o in data.orders})

    teams: List[TeamData] = [TeamData(team_id=t_id) for t_id in team_ids]
    products: List[ProductData] = [ProductData(product_id=p_id) for p_id in product_ids]

    # ---- 2. Агрегируем производительность по (team_id, product_id) ----
    prod_map: Dict[Tuple[int, int], Dict[str, float]] = {}

    for tp in data.team_productivity:
        key = (tp.team_id, tp.product_id)
        entry = prod_map.setdefault(key, {"serial_rate": 0.0, "non_serial_rate": 0.0})

        if tp.production_type == "serial":
            entry["serial_rate"] = tp.productivity
        else:
            entry["non_serial_rate"] = tp.productivity

    prepared_prod: List[PreparedTeamProductivity] = []
    for (team_id, product_id), rates in prod_map.items():
        prepared_prod.append(
            PreparedTeamProductivity(
                team_id=team_id,
                product_id=product_id,
                serial_rate=rates["serial_rate"],
                non_serial_rate=rates["non_serial_rate"],
            )
        )

    # ---- 3. H_jd: всегда 8 часов, без уменьшения ----
    H_jd: Dict[Tuple[int, int], float] = {}
    for team_id in team_ids:
        for d in range(1, num_days + 1):
            H_jd[(team_id, d)] = BASE_HOURS_PER_DAY

    # ---- 4. t_ojd: часы на единицу продукции с учётом буфера через производительность ----
    t_ojd: Dict[Tuple[int, int, int], float] = {}

    for o in data.orders:
        for team_id in team_ids:
            rates = prod_map.get((team_id, o.product_id))
            if rates is None:
                continue

            base_rate = (
                rates["serial_rate"]
                if o.production_type == "serial"
                else rates["non_serial_rate"]
            )

            if base_rate is None or base_rate <= 0:
                continue

            for d in range(1, num_days + 1):
                current_date = start_date + timedelta(days=d - 1)
                month = current_date.month
                delta = DELTA_BY_MONTH.get(month, DEFAULT_DELTA)

                if d == 1:
                    eff_multiplier = 1.0
                else:
                    eff_multiplier = max(0.0, 1.0 - delta)

                eff_rate = base_rate * eff_multiplier

                if eff_rate <= 0:
                    continue

                hours_per_unit = 1.0 / eff_rate
                t_ojd[(o.order_id, team_id, d)] = hours_per_unit

    # ---- 5. Подготовка заказов (дедлайны в днях от start_date) ----
    prepared_orders: List[PreparedOrder] = []
    for idx, o in enumerate(data.orders):
        deadline_days = (o.deadline_date - start_date).days
        if deadline_days < 0:
            deadline_days = 0

        prepared_orders.append(
            PreparedOrder(
                index=idx,
                order_id=o.order_id,
                product_id=o.product_id,
                production_type=o.production_type,
                quantity=o.quantity,
                deadline=deadline_days,
            )
        )

    # ---- 6. Список дат горизонта ----
    day_list = [start_date + timedelta(days=i) for i in range(num_days)]

    # ---- 7. Собираем PreparedInput ----
    prep = PreparedInput(
        orders=prepared_orders,
        teams=teams,
        products=products,
        productivity=prepared_prod,
        start_date=start_date,
        num_days=num_days,
        t_ojd=t_ojd,
        H_jd=H_jd,
        params=data.params,  # здесь лежат k_tardy_default, k_under, k_over, alpha, beta
        day_list=day_list,
    )

    return prep


def run_model_a(payload: OptimizationRequestModelA) -> OptimizationResponseModelA:
    prepared = build_optimization_input(payload)
    result: OptimizationResult = solve_model_a(prepared)
    return OptimizationResponseModelA.model_validate(result.model_dump())


def run_model_b(payload: OptimizationRequestModelB) -> OptimizationResponseModelB:
    prepared = build_optimization_input(payload)

    alpha = payload.params.alpha
    beta = payload.params.beta

    result: OptimizationResult = solve_model_b(prepared, alpha, beta)
    return OptimizationResponseModelB.model_validate(result.model_dump())
