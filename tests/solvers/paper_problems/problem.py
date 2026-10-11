"""This module holds `PaperProblem`, the dataclass that every solver's tests use to define a published test problem,
`PaperProblemEnum`, the base of the enums that hold a published table shared by several solvers, and
`UNSTATED_RUN_DETAILS`, the reason for a deviation of 1 that has no cause of its own."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import Enum

import pytest

from sunnbear.solvers import SolveResult, SolveStatus


@dataclass(frozen=True)
class PaperProblem:
    """`PaperProblem` is 1 published test problem: a function, its interval, and a solver's published results on it.

    Where a paper prints a count in another form, such as iterations that exclude the 2 evaluations at the interval
    bounds, the code that defines the problem converts it to an evaluation count, and writes the conversion out so
    that the printed number stays visible, for example ``n_fevals=n_iterations + 2``.

    Attributes:
        name: The paper's label for the problem; also its pytest id.
        root: The published root, or None where the paper gives none.
        root_rel_tol: The relative tolerance on ``root``, set from the digits that the paper prints.
        root_abs_tol: The absolute tolerance on ``root``, set from the digits that the paper prints; with both
            tolerances at their default of 0, the root must match exactly.
        n_fevals: The published evaluation count in sunnbear's counting, which includes the 2 evaluations at the
            interval bounds, or None where the paper gives none.
        n_fevals_strict_lower_bound: A strict lower bound on the solve's evaluation count, in sunnbear's counting,
            where the paper prints only a lower bound, such as "200+"; None otherwise. At most 1 of ``n_fevals`` and
            ``n_fevals_strict_lower_bound`` is set.
        n_fevals_tol: How far the solve's evaluation count may lie from ``n_fevals``; None when the solve's
            evaluation count is not checked.
        deviation_reason: Why the solve's evaluation count does not reproduce ``n_fevals`` exactly; required whenever
            ``n_fevals_tol`` is not 0, and None when it is 0. A deviation of 1 may give `UNSTATED_RUN_DETAILS`.
        deviation_observation: What the solve does differently from the published run, such as "the solve reaches
            f(x) == 0 one iteration early"; optional, and only beside a ``deviation_reason``.
    """

    name: str
    f: Callable[[float], float]
    a: float
    b: float
    root: float | None = None
    root_rel_tol: float = 0.0
    root_abs_tol: float = 0.0
    n_fevals: int | None = None
    n_fevals_strict_lower_bound: int | None = None
    n_fevals_tol: int | None = 0
    deviation_reason: str | None = None
    deviation_observation: str | None = None

    def __post_init__(self) -> None:
        """Check that a deviation_reason is given exactly when the count is not reproduced exactly, that an observation
        comes only with a reason, and that at most 1 of the published count and its lower bound is set."""
        if (self.n_fevals_tol != 0) != (self.deviation_reason is not None):
            raise ValueError(f"{self.name}: give a deviation_reason exactly when n_fevals_tol is not 0.")
        if self.deviation_observation is not None and self.deviation_reason is None:
            raise ValueError(f"{self.name}: give a deviation_observation only beside a deviation_reason.")
        if self.n_fevals is not None and self.n_fevals_strict_lower_bound is not None:
            raise ValueError(f"{self.name}: set at most 1 of n_fevals and n_fevals_strict_lower_bound.")

    def __str__(self) -> str:
        """Return the problem's name, so that ``ids=str`` labels each pytest case with it."""
        return self.name

    def assert_reproduced_by(self, result: SolveResult) -> None:
        """Assert that a solve reproduces the problem's published results:

        - it converges;
        - it returns the published root within the root's tolerances, where the paper gives one;
        - its evaluation count reproduces the published one, as `assert_n_fevals_reproduced` checks.
        """
        assert result.status is SolveStatus.CONVERGED
        if self.root is not None:
            assert result.x == pytest.approx(self.root, rel=self.root_rel_tol, abs=self.root_abs_tol)
        self.assert_n_fevals_reproduced(result.n_fevals)

    def assert_n_fevals_reproduced(self, solve_n_fevals: int) -> None:
        """Assert that the evaluation count at which a solve stops reproduces the published count:

        - it lies within ``n_fevals_tol`` of ``n_fevals``, where the count is checked;
        - it exceeds ``n_fevals_strict_lower_bound`` instead, where the paper prints only a lower bound.
        """
        if self.n_fevals_strict_lower_bound is not None:
            assert solve_n_fevals > self.n_fevals_strict_lower_bound
        elif self.n_fevals is not None and self.n_fevals_tol is not None:
            assert abs(solve_n_fevals - self.n_fevals) <= self.n_fevals_tol


# ==================================================================================================
#  PaperProblemEnum
# ==================================================================================================
class PaperProblemEnum(Enum):
    """`PaperProblemEnum` is the base of an enum that holds the problems of 1 published table that several solvers
    reproduce: each member's value is 1 problem of the table, without results, and the methods below return it with 1
    solver's published results.

    A solver's tests then list the table as 1 line per row, such as
    ``FordTable4Problem.F1_I1.with_n_iterations(10)``.
    """

    def with_n_iterations(
        self, n_iterations: int, *, deviation: int = 0, reason: str | None = None, observation: str | None = None
    ) -> PaperProblem:
        """Return the member's problem with a published iteration count, which excludes the 2 evaluations at the
        interval bounds.

        Args:
            n_iterations: The published iteration count.
            deviation: How far the solve's count may lie from the published one; 0 when it must match exactly.
            reason: Why the count deviates; required when ``deviation`` is not 0.
            observation: What the solve does differently from the published run; optional, beside a ``reason``.
        """
        return replace(
            self.value,
            n_fevals=n_iterations + 2,
            n_fevals_tol=deviation,
            deviation_reason=reason,
            deviation_observation=observation,
        )

    def with_n_iterations_above(self, n_iterations: int) -> PaperProblem:
        """Return the member's problem for a row that the paper prints only as more than ``n_iterations`` iterations,
        such as "200+"."""
        return replace(self.value, n_fevals_strict_lower_bound=n_iterations + 2)


# ==================================================================================================
#  Deviation reasons
# ==================================================================================================
# `UNSTATED_RUN_DETAILS` is the reason for a count that deviates by 1 without a cause of its own. A published count
# depends on details of the published run that a paper does not state, and any of them can shift a count by 1:
# - the arithmetic and its rounding;
# - the math library (``pow``, ``exp``, ``log``, ...);
# - the programming language and its compiler;
# - the many micro-decisions that an implementation involves, too numerous or tedious to state in a paper.
# A deviation larger than 1 needs a cause of its own.
UNSTATED_RUN_DETAILS = (
    "unstated run details: a detail of the published run that the paper does not state, such as its arithmetic, its "
    "math library, its programming language or one of the many micro-decisions of its implementation, can shift a "
    "count by 1"
)
