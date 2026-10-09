"""This module holds `PaperProblem`, the dataclass that every solver's tests use to define a published test problem."""

from collections.abc import Callable
from dataclasses import dataclass

import pytest

from sunnbear.solvers import SolveResult, SolveStatus


@dataclass(frozen=True)
class PaperProblem:
    """`PaperProblem` is 1 published test problem: a function, its interval, and a solver's published results on it.

    A count that the paper prints in another form, such as iterations without the 2 evaluations at the interval
    bounds, is converted to an evaluation count where the problem is defined, written so that the printed number stays
    visible, for example ``n_fevals=n_iterations + 2``.

    Attributes:
        name: The paper's label for the problem; also its pytest id.
        root: The published root, or None where the paper gives none.
        root_rel_tol: The relative tolerance on ``root``, set from the digits that the paper prints.
        root_abs_tol: The absolute tolerance on ``root``, set from the digits that the paper prints.
        n_fevals: The published evaluation count in sunnbear's counting, which includes the 2 evaluations at the
            interval bounds, or None where the paper gives none.
        n_fevals_tol: How far the solve's evaluation count may lie from ``n_fevals``; None when that count is not
            checked.
        deviation_reason: Why the solve's evaluation count does not reproduce ``n_fevals`` exactly; required whenever
            ``n_fevals_tol`` is not 0.
    """

    name: str
    f: Callable[[float], float]
    a: float
    b: float
    root: float | None = None
    root_rel_tol: float = 0.0
    root_abs_tol: float = 0.0
    n_fevals: int | None = None
    n_fevals_tol: int | None = 0
    deviation_reason: str | None = None

    def __post_init__(self) -> None:
        """Check that a count that is not reproduced exactly comes with its reason."""
        if (self.n_fevals_tol != 0) != (self.deviation_reason is not None):
            raise ValueError(f"{self.name}: give a deviation_reason exactly when n_fevals_tol is not 0.")

    def __str__(self) -> str:
        """Return the problem's name, so that ``ids=str`` labels each pytest case with it."""
        return self.name

    def assert_reproduced_by(self, result: SolveResult) -> None:
        """Assert that a solve reproduces the problem's published results:

        - it converges;
        - it returns the published root within the root's tolerances, where the paper gives one;
        - it evaluates as often as published, within ``n_fevals_tol``, where the count is checked.
        """
        assert result.status is SolveStatus.CONVERGED
        if self.root is not None:
            assert result.x == pytest.approx(self.root, rel=self.root_rel_tol, abs=self.root_abs_tol)
        if self.n_fevals is not None and self.n_fevals_tol is not None:
            assert abs(result.n_fevals - self.n_fevals) <= self.n_fevals_tol
