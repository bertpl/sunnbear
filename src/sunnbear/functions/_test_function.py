"""Materialized test functions: `CandidateTestFunction` (pre-calibration) and `TestFunction`.

The two types differ by exactly one fact: whether a valid c-range has been
established. Keeping them separate makes "calibrated" a property of the type
rather than of a nullable field, so code that requires a benchmarkable
function cannot silently receive an uncalibrated one.
"""

from dataclasses import dataclass

from ._identity import FunctionId
from ._types import XCFun, XFun


# ==================================================================================================
#  CandidateTestFunction
# ==================================================================================================
@dataclass(frozen=True)
class CandidateTestFunction:
    """A materialized formula instance whose c-range is not (yet) established.

    Attributes:
        id: Stable identity (formula number + bound parameter tuple).
        fun: The ``f(x, c)`` callable with the parameter tuple already bound.
        a: Lower end of the bracketing x-interval.
        b: Upper end of the bracketing x-interval.
    """

    id: FunctionId
    fun: XCFun
    a: float
    b: float


# ==================================================================================================
#  TestFunction
# ==================================================================================================
@dataclass(frozen=True)
class TestFunction:
    """A benchmarkable test function: ``f(x, c)``, its bracket, and its calibrated c-range.

    For every ``c`` in ``[c_min, c_max]``, ``f(a, c) * f(b, c) < 0`` and the
    function returns finite values on ``[a, b]``.
    """

    id: FunctionId
    fun: XCFun
    a: float
    b: float
    c_min: float
    c_max: float

    def bind(self, c: float) -> XFun:
        """Return the single-argument ``f(x)`` with `c` bound, e.g. for handing to a solver."""
        fun = self.fun

        def f(x: float) -> float:
            """Evaluate the test function at `x` with the bound Monte-Carlo parameter."""
            return fun(x, c)

        return f
