"""This module holds `PaperProblem`, the form of every published test problem that a solver's tests reproduce."""

from collections.abc import Callable
from dataclasses import dataclass

import pytest

from sunnbear.solvers import SolveResult, SolveStatus


@dataclass(frozen=True)
class PaperProblem:
    """`PaperProblem` is 1 published test problem: a function, its interval, and the results that a paper publishes
    for a solver on it.

    Each solver's tests hold their own list of problems, with that solver's published results. A problem set that the
    papers of several solvers use is shared as problems without results.

    A count that the paper prints in another form, such as iterations without the 2 evaluations at the interval
    bounds, is converted where the problem is defined, and the printed number stays visible there, for example
    ``n_fevals=n_iterations + 2``.

    Attributes:
        name: The paper's label for the problem; also its pytest id.
        root: The published root, or None where the paper gives none.
        root_rel_tol: The relative tolerance on ``root``, set from the digits that the paper prints.
        root_abs_tol: The absolute tolerance on ``root``, set from the digits that the paper prints.
        n_fevals: The published evaluation count in sunnbear's counting, which includes the 2 evaluations at the
            interval bounds, or None where the paper gives none.
        n_fevals_tol: How far the count may lie from ``n_fevals``; None when the count is not checked.
        deviation: Why the count is not reproduced exactly; required whenever ``n_fevals_tol`` is not 0.
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
    deviation: str | None = None

    def __post_init__(self) -> None:
        """Check that a count that is not reproduced exactly comes with its reason."""
        if (self.n_fevals_tol != 0) != (self.deviation is not None):
            raise ValueError(f"{self.name}: give a deviation exactly when n_fevals_tol is not 0.")

    def __str__(self) -> str:
        """Return the problem's name, so that ``ids=str`` labels each pytest case with it."""
        return self.name

    def assert_reproduced_by(self, result: SolveResult) -> None:
        """Assert that a solve reproduces the problem's published results: it converges, returns the published root
        within the root's tolerances where the paper gives one, and evaluates as often as published where the count is
        checked."""
        assert result.status is SolveStatus.CONVERGED
        if self.root is not None:
            assert result.x == pytest.approx(self.root, rel=self.root_rel_tol, abs=self.root_abs_tol)
        if self.n_fevals is not None and self.n_fevals_tol is not None:
            assert abs(result.n_fevals - self.n_fevals) <= self.n_fevals_tol
