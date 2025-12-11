from app.domain.optimization.dto import PreparedInput, OptimizationResult
from app.domain.optimization.model_ab import _solve_core


def solve_model_a(prep: PreparedInput) -> OptimizationResult:
    return _solve_core(prep, alpha=1.0, beta=1.0)
