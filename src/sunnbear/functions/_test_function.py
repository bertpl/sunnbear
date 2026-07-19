"""Materialized test functions: `CandidateTestFunction` (pre-calibration) and `TestFunction`.

The two types differ by exactly one fact: whether a valid c-range has been
established. Keeping them separate makes "calibrated" a property of the type
rather than of a nullable field, so code that requires a benchmarkable
function cannot silently receive an uncalibrated one.

Both carry the originating `Formula` plus their identity rather than a pre-bound
callable. The callable forms are derived from those on demand — ``f(x, c)`` as
`xc_fun`, and the univariate ``f(x)`` as `TestFunction.build_x_fun` — each a
single closure over the formula's once-compiled body, so the solver hot path
never pays for a wrapper around a wrapper.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._identity import FunctionId
from ._types import XCFun, XFun

if TYPE_CHECKING:  # type-only: _formula imports this module at runtime, so the edge cannot be mutual
    from ._formula import Formula


# ==================================================================================================
#  CandidateTestFunction
# ==================================================================================================
@dataclass(frozen=True)
class CandidateTestFunction:
    """A materialized formula instance whose c-range is not (yet) established.

    Attributes:
        id: Stable identity (formula number + bound parameter tuple).
        formula: The formula this was materialized from — supplies the compiled body.
        a: Lower end of the bracketing x-interval.
        b: Upper end of the bracketing x-interval.
    """

    id: FunctionId
    formula: "Formula"
    a: float
    b: float

    @property
    def xc_fun(self) -> XCFun:
        """The ``f(x, c)`` callable, with this candidate's parameter tuple bound."""
        return self.formula.bind_xc_fun(self.id.param_values)

    def calibrated(self, c_min: float, c_max: float) -> "TestFunction":
        """Promote to a `TestFunction` by attaching a calibrated c-range.

        The c-range is the one fact separating the two types, so this method
        is the only way to cross that line — calibration results are always
        supplied from outside, never derived here.
        """
        return TestFunction(id=self.id, formula=self.formula, a=self.a, b=self.b, c_min=c_min, c_max=c_max)


# ==================================================================================================
#  TestFunction
# ==================================================================================================
@dataclass(frozen=True)
class TestFunction:
    """A benchmarkable test function: ``f(x, c)``, its bracket, and its calibrated c-range.

    For every ``c`` in ``[c_min, c_max]``, ``f(a, c) * f(b, c) < 0`` and the
    function returns finite values on ``[a, b]``.

    Attributes:
        id: Stable identity (formula number + bound parameter tuple).
        formula: The formula this was materialized from — supplies the compiled body.
        a: Lower end of the bracketing x-interval.
        b: Upper end of the bracketing x-interval.
        c_min: Lower end of the calibrated c-range.
        c_max: Upper end of the calibrated c-range.
    """

    id: FunctionId
    formula: "Formula"
    a: float
    b: float
    c_min: float
    c_max: float

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
