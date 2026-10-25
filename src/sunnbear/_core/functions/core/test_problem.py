"""Materialized test problems: `CandidateTestProblem` (pre-calibration) and `TestProblem`.

The two types differ by exactly one fact: whether a valid c-range has been
established. Keeping them separate makes "calibrated" a property of the type
rather than of a nullable field, so code that requires a benchmarkable
function cannot silently receive an uncalibrated one.

Both carry the originating `Formula` plus their identity rather than a pre-bound
callable. The callable forms are derived from those on demand — ``f(x, c)`` as
`xc_fun`, and the univariate ``f(x)`` as `TestProblem.build_x_fun` — each a
single closure over the formula's once-compiled body, so the solver hot path
never pays for a wrapper around a wrapper.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .identity import ProblemId
from .types import XCFun, XFun

if TYPE_CHECKING:  # type-only: formula imports this module at runtime, so the edge cannot be mutual
    from .formula import Formula


# ==================================================================================================
#  CandidateTestProblem
# ==================================================================================================
@dataclass(frozen=True)
class CandidateTestProblem:
    """A materialized formula instance whose c-range is not (yet) established.

    Attributes:
        id: Stable identity (formula number + named parameter values).
        formula: The formula this was materialized from — supplies the compiled body.
        a: Lower end of the bracketing x-interval.
        b: Upper end of the bracketing x-interval.
    """

    id: ProblemId
    formula: "Formula"
    a: float
    b: float

    def __post_init__(self) -> None:
        """Reject an ill-defined x-interval: a test problem needs a genuine one, so strictly a < b."""
        if not self.a < self.b:
            raise ValueError(f"Interval must satisfy a < b (got a={self.a}, b={self.b}).")

    @property
    def xc_fun(self) -> XCFun:
        """The ``f(x, c)`` callable, with this candidate's parameter tuple bound."""
        return self.formula.bind_xc_fun(self.id.param_values)

    def calibrated(self, c_min: float, c_max: float) -> "TestProblem":
        """Promote to a `TestProblem` by attaching a calibrated c-range.

        The c-range is the one fact separating the two types, so this method
        is the only way to cross that line — calibration results are always
        supplied from outside, never derived here.
        """
        return TestProblem(id=self.id, formula=self.formula, a=self.a, b=self.b, c_min=c_min, c_max=c_max)


# ==================================================================================================
#  TestProblem
# ==================================================================================================
@dataclass(frozen=True)
class TestProblem:
    """A benchmarkable test problem: ``f(x, c)``, its x-interval, and its calibrated c-range.

    The benchmark samples ``c`` within ``[c_min, c_max]``. The benchmark suite pipeline calibrates
    the c-range so that ``f(a, c)`` and ``f(b, c)`` are finite and of opposite signs at every c-value
    that the benchmark samples.

    Attributes:
        id: Stable identity (formula number + named parameter values).
        formula: The formula this was materialized from — supplies the compiled body.
        a: Lower end of the bracketing x-interval.
        b: Upper end of the bracketing x-interval.
        c_min: Lower end of the calibrated c-range.
        c_max: Upper end of the calibrated c-range.
    """

    id: ProblemId
    formula: "Formula"
    a: float
    b: float
    c_min: float
    c_max: float

    def __post_init__(self) -> None:
        """Reject ill-defined intervals: both the x-interval and the c-range must be genuine, strictly ordered."""
        if not self.a < self.b:
            raise ValueError(f"Interval must satisfy a < b (got a={self.a}, b={self.b}).")
        if not self.c_min < self.c_max:
            raise ValueError(f"Calibrated c-range must satisfy c_min < c_max (got {self.c_min}..{self.c_max}).")

    @property
    def xc_fun(self) -> XCFun:
        """The ``f(x, c)`` callable, with this function's parameter tuple bound."""
        return self.formula.bind_xc_fun(self.id.param_values)

    def build_x_fun(self, c: float) -> XFun:
        """Return the univariate ``f(x)`` for a fixed `c` — what a solver consumes.

        One closure binding both the parameter tuple and `c` over the compiled
        body, rather than a wrapper around `xc_fun`: on the hot path that is a
        single Python call per evaluation instead of two.
        """
        return self.formula.bind_x_fun(self.id.param_values, c)
