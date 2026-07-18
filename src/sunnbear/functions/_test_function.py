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

    def calibrated(self, c_min: float, c_max: float) -> "TestFunction":
        """Promote to a `TestFunction` by attaching a calibrated c-range.

        The c-range is the one fact separating the two types, so this method
        is the only way to cross that line — calibration results are always
        supplied from outside, never derived here.
        """
        return TestFunction(id=self.id, fun=self.fun, a=self.a, b=self.b, c_min=c_min, c_max=c_max)


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

    def univariate_fun(self, c: float) -> XFun:
        """Return the univariate ``f(x)`` for a fixed `c` — what a solver consumes.

        A closure rather than `functools.partial`: `c` is the *second*
        argument, so partial could only bind it by keyword, which measures
        noticeably slower than this closure (binding it positionally would
        require an ``f(c, x)`` signature, against the framework's ``f(x, c)``
        convention).
        """
        fun = self.fun

        def f(x: float) -> float:
            """Evaluate the test function at `x` with the bound Monte-Carlo parameter."""
            return fun(x, c)

        return f
