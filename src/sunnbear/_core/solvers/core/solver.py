"""`Solver` with its template method, and `BracketingSolver`, are the solver base classes.

Everything that makes a solve measurable lives in `Solver.solve` and the
`WrappedFunction` it installs; a subclass writes only the algorithm.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import ClassVar, Generic

from counted_float import CountedFloat, FlopCountingContext

# `typing.TypeVar` accepts `default=` only from Python 3.13; this project supports 3.11 and 3.12 too.
from typing_extensions import TypeVar

from .exceptions import DivergedError, FunctionDomainError, MaxFevalsExceeded
from .interval import Interval
from .result import SolveResult, SolveStatus
from .state import SolveState
from .wrapped_function import WrappedFunction

# A solver with fields of its own binds StateT to its SolveState subclass; see `Solver.state_cls`.
StateT = TypeVar("StateT", bound=SolveState, default=SolveState)


# ==================================================================================================
#  Solver
# ==================================================================================================
class Solver(ABC, Generic[StateT]):
    """`Solver` is the base class every benchmarkable root solver subclasses.

    A subclass implements `_solve` and takes its configuration through
    ``__init__``; `solve` has a fixed signature, so all solvers are driven
    identically. Instances are immutable configuration, safe to share across
    solves: everything that changes during a solve lives in the `SolveState`
    that `solve` creates and hands to the algorithm.

    Class attributes:
        name: Canonical identifier fragment, e.g. ``"bisection"``; with
            `version` and the init arguments, the name identifies a solver in
            benchmark results.
        version: Bumped on any behavior change, so results from different
            versions of one solver are never combined unknowingly.
        state_cls: The `SolveState` class that `solve` instantiates. A solver
            that carries values between iterations names its own subclass here
            and binds ``StateT`` to it; a memoryless solver leaves ``state_cls`` and ``StateT`` at their defaults.
    """

    name: ClassVar[str]
    version: ClassVar[int]
    state_cls: ClassVar[type[SolveState]] = SolveState

    # --------------------------------------------------------------------------
    #  Template method
    # --------------------------------------------------------------------------
    def solve(
        self,
        f: Callable[[float], float],
        a: float,
        b: float,
        *,
        xtol: float,
        max_fevals: int,
        history_enabled: bool = False,
    ) -> SolveResult:
        """Find a root of ``f`` in ``[a, b]`` and report what the solve did.

        - ``f(a)`` and ``f(b)`` are evaluated first; an interval bound whose function value is exactly
          zero ends the solve as ``CONVERGED`` without running the algorithm. A failure at an interval
          bound is recorded like any other: nothing raised by ``f`` reaches the caller.
        - The interval handed to the solver is an `IncreasingInterval` or a `DecreasingInterval`,
          whichever the function values at the interval bounds hold; a solver that supports one
          orientation only decides for itself what to do with the other.
        - Every abnormal ending becomes a `SolveStatus`, not an exception: ``solve()`` is invoked
          at scale during benchmarks and must not interrupt the pipeline.
        - Divergence is judged by where things ended: a solve whose result lies outside ``[a, b]``,
          or whose function error happened outside ``[a, b]``, is ``DIVERGED``. Excursions that
          return are not penalized.
        - The validation before the flop-counting context and the divergence checks after it are
          uncounted. Everything inside the context runs on `CountedFloat` and is counted: the
          zero and sign checks on ``f(a)`` and ``f(b)``, ``xtol``, the bookkeeping of the best
          estimate, and the solver's arithmetic. An early exit therefore reports the comparisons
          that produced it.

        Args:
            f: The function; must be finite on ``[a, b]``, with ``f(a)`` and ``f(b)`` of opposite sign or zero.
            a: Lower bound of the interval.
            b: Upper bound of the interval.
            xtol: Requested x-tolerance, ``|x_true - x| <= xtol``.
            max_fevals: Function-evaluation budget, the 2 evaluations at the interval bounds included.
            history_enabled: Whether to keep every ``(x, f(x))`` pair in the result.

        Raises:
            ValueError: If ``a >= b``, or ``f(a)`` and ``f(b)`` have the same sign and neither is
                zero — a caller error, not a solve outcome.
        """
        # --- uncounted validation -------------------
        if not a < b:
            raise ValueError(f"Interval must satisfy a < b (got a={a}, b={b}).")
        wrapped_f = WrappedFunction(f, max_fevals=max_fevals, history_enabled=history_enabled)

        # --- counted: main algorithm ----------------
        x_failed: float | None = None  # Where f failed, if it did; decides FUNCTION_ERROR versus DIVERGED below.
        with FlopCountingContext() as flop_ctx:
            # --- prep and early exits ---------------
            a_counted, b_counted, xtol_counted = CountedFloat(a), CountedFloat(b), CountedFloat(xtol)
            try:
                fa, fb = wrapped_f(a_counted), wrapped_f(b_counted)
            except Exception as exc:  # noqa: BLE001 — a failure at an interval bound is recorded like any other
                x, status, x_failed = _ending_of(exc, x_best=0.5 * (a_counted + b_counted))
            else:
                if fa == 0.0:  # Early exit when a is a root.
                    x, status = a_counted, SolveStatus.CONVERGED
                elif fb == 0.0:  # Early exit when b is a root.
                    x, status = b_counted, SolveStatus.CONVERGED
                else:
                    # --- actual solve -----------------------
                    interval = Interval.from_interval_bounds(a_counted, b_counted, fa, fb)
                    state = self.state_cls(f=wrapped_f, interval=interval, xtol=xtol_counted, x_best=interval.midpoint)
                    try:
                        # state_cls is typed as type[SolveState]: the checker sees SolveState where StateT is expected.
                        x, status = self._solve(state), SolveStatus.CONVERGED  # type: ignore[arg-type]
                    except Exception as exc:  # noqa: BLE001 — every ending becomes a recorded status, by design
                        x, status, x_failed = _ending_of(exc, x_best=state.x_best)

        # --- return results -------------------------
        # Divergence is the framework's judgment, not solver work, so these checks are uncounted.
        x_plain = float(x)
        if x_failed is not None and not a <= x_failed <= b:
            # A well-formed problem only guarantees that f can be evaluated on [a, b], so a failure
            # outside is attributed to divergence.
            status = SolveStatus.DIVERGED
        elif status is not SolveStatus.SOLVER_ERROR and not a <= x_plain <= b:
            # Any final x outside [a, b] not connected to a solver error is also a divergence.
            status = SolveStatus.DIVERGED
        return SolveResult(
            x=x_plain,
            status=status,
            n_fevals=wrapped_f.n_fevals,
            flop_counts=flop_ctx.flop_counts(),
            history=None if wrapped_f.history is None else tuple(wrapped_f.history),
        )

    # --------------------------------------------------------------------------
    #  Subclass hook
    # --------------------------------------------------------------------------
    @abstractmethod
    def _solve(self, state: StateT) -> float:
        """Run the algorithm on `state` and return the root estimate.

        - Evaluate the function only through ``state.f``, and let its interrupts propagate.
        - Keep ``state.x_best`` current, so an interrupted solve still reports a meaningful ``x``.
        """


# ==================================================================================================
#  BracketingSolver
# ==================================================================================================
class BracketingSolver(Solver[StateT]):
    """`BracketingSolver` is the base class for interval-reducing solvers; a subclass implements one `_next_x`.

    A bracketing solver is defined by what it does each iteration: pick a point inside the interval,
    evaluate the function there, and keep the half that still holds the sign change.

    The base class owns the evaluation and the split; only the choice of the point is left to the
    subclass. It cannot evaluate the function itself, split the interval wrongly, or define a wrong
    stopping criterion (`Interval.is_converged`); the base class does all three.

    One `_next_x` is one iteration. A solver that carries values between iterations keeps them on its
    `SolveState` subclass (see `Solver.state_cls`). A solver whose iteration evaluates the function
    more than once, or updates the interval in its own way, overrides `_solve` on `Solver` directly,
    instead of implementing `_next_x`.
    """

    def _solve(self, state: StateT) -> float:
        """Split the interval at `_next_x` until `Interval.is_converged` holds; return `Interval.root`."""
        interval = state.interval
        xtol_doubled = 2.0 * state.xtol
        while not interval.is_converged(xtol_doubled):
            x = self._next_x(state, interval)
            interval = interval.split_at(x, state.f(x))
            state.x_best = x  # This is the last evaluated point, so a stalled solver still reports its best estimate.
        return interval.root()

    @abstractmethod
    def _next_x(self, state: StateT, interval: Interval) -> float:
        """Return the interval's next evaluation point, strictly inside ``interval``.

        Read the function values at the interval bounds from ``interval``, and any value carried
        between iterations from ``state``; do not evaluate the function here.
        """


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _ending_of(exc: Exception, x_best: float) -> tuple[float, SolveStatus, float | None]:
    """Return the root estimate, the status, and where ``f`` failed (if it did) for a solve that ended in ``exc``.

    Anything but a `SolveException` is a solver bug, recorded as ``SOLVER_ERROR``.
    """
    if isinstance(exc, MaxFevalsExceeded):
        return x_best, SolveStatus.MAX_FEVALS, None
    elif isinstance(exc, DivergedError):
        return x_best, SolveStatus.DIVERGED, None
    elif isinstance(exc, FunctionDomainError):
        return x_best, SolveStatus.FUNCTION_ERROR, exc.x
    else:
        return x_best, SolveStatus.SOLVER_ERROR, None
