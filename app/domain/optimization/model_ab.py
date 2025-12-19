import cvxpy as cp
from typing import Dict, List, Tuple

from app.domain.optimization.dto import (
    PreparedInput,
    OptimizationResult,
    TeamDayPlan,
    DayTask,
)


def _solve_core(prep: PreparedInput, alpha: float, beta: float) -> OptimizationResult:
    orders = prep.orders
    teams = prep.teams
    t_ojd = prep.t_ojd
    H_jd = prep.H_jd
    num_days = prep.num_days
    day_list = prep.day_list
    params = prep.params

    k_tardy = float(params.k_tardy_default)
    k_under = float(params.k_under)
    k_over = float(params.k_over)

    order_index: Dict[int, int] = {o.order_id: o.index for o in orders}
    team_index: Dict[int, int] = {t.team_id: i for i, t in enumerate(teams)}

    num_orders = len(orders)
    num_teams = len(teams)

    # --- 2D variable: x[order, k], where k = team_idx * num_days + day_idx
    K = num_teams * num_days
    x = cp.Variable((num_orders, K), nonneg=True)

    T = cp.Variable(num_orders, nonneg=True)
    U = cp.Variable((num_teams, num_days), nonneg=True)
    P = cp.Variable((num_teams, num_days), nonneg=True)

    def _k(j_idx: int, d_idx: int) -> int:
        return j_idx * num_days + d_idx

    constraints = []

    # --- Fulfillment: sum_{j,d} x[o,j,d] >= Q_o
    for o in orders:
        oi = order_index[o.order_id]
        constraints.append(cp.sum(x[oi, :]) >= float(o.quantity))

    # --- Time balance per team/day: sum_o t[o,j,d] * x[o,j,d] + U - P = H
    for team in teams:
        j_idx = team_index[team.team_id]
        team_id = team.team_id

        for d in range(1, num_days + 1):
            d_idx = d - 1
            H = float(H_jd.get((team_id, d), 0.0))
            k = _k(j_idx, d_idx)

            hours_expr = 0.0
            for o in orders:
                oi = order_index[o.order_id]
                tij = t_ojd.get((o.order_id, team_id, d))
                if tij is None:
                    continue
                hours_expr += float(tij) * x[oi, k]

            constraints.append(hours_expr + U[j_idx, d_idx] - P[j_idx, d_idx] == H)

            # Overtime cap: P <= H (max +1 shift)
            constraints.append(P[j_idx, d_idx] <= H)

    # --- Tardiness via weighted-average completion day
    for o in orders:
        oi = order_index[o.order_id]
        q = float(o.quantity)

        if q <= 0:
            constraints.append(T[oi] >= 0.0)
            continue

        completion_expr = 0.0
        for team in teams:
            j_idx = team_index[team.team_id]
            for d in range(1, num_days + 1):
                d_idx = d - 1
                completion_expr += float(d) * x[oi, _k(j_idx, d_idx)]

        completion_expr = completion_expr / q
        constraints.append(T[oi] >= completion_expr - float(o.deadline))
        constraints.append(T[oi] >= 0.0)

    # --- Objective
    objective = 0.0

    # tardiness penalty
    objective += k_tardy * cp.sum(cp.square(T))

    # small preference to earlier production (linear term)
    TIME_PENALTY = 0.001
    time_cost = 0.0
    for o in orders:
        oi = order_index[o.order_id]
        for team in teams:
            j_idx = team_index[team.team_id]
            for d in range(1, num_days + 1):
                d_idx = d - 1
                time_cost += float(d) * x[oi, _k(j_idx, d_idx)]

    objective += TIME_PENALTY * time_cost

    # underutilization and overtime penalties
    if k_under > 0:
        objective += float(alpha) * k_under * cp.sum(cp.square(U))
    if k_over > 0:
        objective += float(beta) * k_over * cp.sum(cp.square(P))

    problem = cp.Problem(cp.Minimize(objective), constraints)

    # OSQP works for convex QP with quadratic objective and linear constraints
    problem.solve(solver="OSQP")

    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise ValueError(f"Optimization failed with status: {problem.status}")

    if x.value is None or T.value is None:
        raise ValueError("Optimization produced no solution values (x or T is None)")

    # --- Build response
    team_day_plans: List[TeamDayPlan] = []

    for team in teams:
        j_idx = team_index[team.team_id]
        team_id = team.team_id

        for d in range(1, num_days + 1):
            d_idx = d - 1
            current_date = day_list[d_idx]
            day_tasks: List[DayTask] = []

            for o in orders:
                oi = order_index[o.order_id]
                qty_val = float(x.value[oi, _k(j_idx, d_idx)])

                if qty_val < 1e-6:
                    continue

                tij = t_ojd.get((o.order_id, team_id, d))
                if tij is None:
                    continue

                hours_val = qty_val * float(tij)

                day_tasks.append(
                    DayTask(
                        day_index=d,
                        work_date=current_date,
                        product_id=o.product_id,
                        production_type=o.production_type,
                        planned_hours=round(hours_val, 2),
                        planned_quantity=round(qty_val, 2),
                    )
                )

            if day_tasks:
                team_day_plans.append(
                    TeamDayPlan(
                        team_id=team_id,
                        day_index=d,
                        work_date=current_date,
                        tasks=day_tasks,
                    )
                )

    order_tardiness: Dict[int, float] = {
        o.order_id: float(T.value[order_index[o.order_id]]) for o in orders
    }

    return OptimizationResult(
        objective_value=float(problem.value),
        team_day_plans=team_day_plans,
        order_tardiness=order_tardiness,
    )
