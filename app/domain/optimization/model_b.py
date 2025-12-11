from app.domain.optimization.dto import PreparedInput, OptimizationResult
from app.domain.optimization.model_ab import _solve_core


def solve_model_b(prep: PreparedInput, alpha: float, beta: float) -> OptimizationResult:
    return _solve_core(prep, alpha=alpha, beta=beta)
