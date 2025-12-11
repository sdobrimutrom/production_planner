import cvxpy as cp
from typing import Dict, List

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

    k_tardy = params.k_tardy_default
    k_under = params.k_under
    k_over = params.k_over

    order_index: Dict[int, int] = {o.order_id: o.index for o in orders}
    team_index: Dict[int, int] = {t.team_id: i for i, t in enumerate(teams)}

    num_orders = len(orders)
    num_teams = len(teams)

    x = cp.Variable((num_orders, num_teams, num_days), nonneg=True)

    T = cp.Variable(num_orders, nonneg=True)

    U = cp.Variable((num_teams, num_days), nonneg=True)
    P = cp.Variable((num_teams, num_days), nonneg=True)

    constraints = []

    for o in orders:
        oi = order_index[o.order_id]

        produced_expr = 0
        for team in teams:
            j_idx = team_index[team.team_id]
            for d in range(1, num_days + 1):
                produced_expr += x[oi, j_idx, d - 1]

        constraints.append(produced_expr >= o.quantity)

    for team in teams:
        j_idx = team_index[team.team_id]
        team_id = team.team_id

        for d in range(1, num_days + 1):
            H = H_jd.get((team_id, d), 0.0)

            hours_expr = 0
            for o in orders:
                oi = order_index[o.order_id]
                tij = t_ojd.get((o.order_id, team_id, d))
                if tij is None:
                    continue
                hours_expr += tij * x[oi, j_idx, d - 1]

            constraints.append(hours_expr + U[j_idx, d - 1] - P[j_idx, d - 1] == H)

            constraints.append(P[j_idx, d - 1] <= H)

    for o in orders:
        oi = order_index[o.order_id]

        if o.quantity <= 0:
            constraints.append(T[oi] >= 0)
            continue

        completion_expr = 0
        for team in teams:
            j_idx = team_index[team.team_id]
            for d in range(1, num_days + 1):
                completion_expr += d * x[oi, j_idx, d - 1]

        completion_expr = completion_expr / o.quantity

        constraints.append(T[oi] >= completion_expr - o.deadline)
        constraints.append(T[oi] >= 0)

    objective = 0.0

    for o in orders:
        oi = order_index[o.order_id]
        objective += k_tardy * cp.square(T[oi])

    TIME_PENALTY = 0.001
    time_cost = 0.0
    for o in orders:
        oi = order_index[o.order_id]
        for team in teams:
            j_idx = team_index[team.team_id]
            for d in range(1, num_days + 1):
                time_cost += d * x[oi, j_idx, d - 1]

    objective += TIME_PENALTY * time_cost
    
    if k_under > 0:
        objective += alpha * k_under * cp.sum(cp.square(U))
    if k_over > 0:
        objective += beta * k_over * cp.sum(cp.square(P))

    problem = cp.Problem(cp.Minimize(objective), constraints)
    problem.solve(solver="OSQP")

    team_day_plans: List[TeamDayPlan] = []

    for team in teams:
        j_idx = team_index[team.team_id]
        team_id = team.team_id

        for d in range(1, num_days + 1):
            current_date = day_list[d - 1]
            day_tasks: List[DayTask] = []

            for o in orders:
                oi = order_index[o.order_id]
                qty_val = x.value[oi, j_idx, d - 1]

                if qty_val is None or qty_val < 1e-6:
                    continue

                tij = t_ojd.get((o.order_id, team_id, d))
                if tij is None:
                    continue

                hours_val = qty_val * tij

                day_tasks.append(
                    DayTask(
                        day_index=d,
                        work_date=current_date,
                        product_id=o.product_id,
                        production_type=o.production_type,
                        planned_hours=round(float(hours_val), 2),
                        planned_quantity=round(float(qty_val), 2),
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
