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

        - ``f(a)`` and ``f(b)`` are evaluated first; a bound whose value is exactly zero ends the
          solve as ``CONVERGED`` without running the algorithm. A failure at a bound is recorded
          like any other: nothing raised by ``f`` reaches the caller.
        - The bracket handed to the solver is an `IncreasingInterval` or a `DecreasingInterval`,
          whichever the endpoint values hold; a solver that supports one orientation only decides
          for itself what to do with the other.
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
            a: Lower end of the bracket.
            b: Upper end of the bracket.
            xtol: Requested x-tolerance, ``|x_true - x| <= xtol``.
            max_fevals: Function-evaluation budget, the 2 endpoint evaluations included.
            history_enabled: Whether to keep every ``(x, f(x))`` pair in the result.

        Raises:
            ValueError: If ``a >= b``, or ``f(a)`` and ``f(b)`` have the same sign and neither is
                zero — a caller error, not a solve outcome.
        """
        # --- uncounted validation -------------------
        if not a < b:
            raise ValueError(f"Bracket must satisfy a < b (got a={a}, b={b}).")
        wrapped_f = WrappedFunction(f, max_fevals=max_fevals, history_enabled=history_enabled)

        # --- counted: main algorithm ----------------
        x_failed: float | None = None  # Where f failed, if it did; decides FUNCTION_ERROR versus DIVERGED below.
        with FlopCountingContext() as flop_ctx:
            # --- prep and early exits ---------------
            a_counted, b_counted, xtol_counted = CountedFloat(a), CountedFloat(b), CountedFloat(xtol)
            try:
                fa, fb = wrapped_f(a_counted), wrapped_f(b_counted)
            except Exception as exc:  # noqa: BLE001 — a failure at a bound is recorded like any other
                x, status, x_failed = _ending_of(exc, x_best=0.5 * (a_counted + b_counted))
            else:
                if fa == 0.0:  # Early exit when a is a root.
                    x, status = a_counted, SolveStatus.CONVERGED
                elif fb == 0.0:  # Early exit when b is a root.
                    x, status = b_counted, SolveStatus.CONVERGED
                else:
                    # --- actual solve -----------------------
                    bracket = Interval.from_endpoints(a_counted, b_counted, fa, fb)
                    state = self.state_cls(f=wrapped_f, bracket=bracket, xtol=xtol_counted, x_best=bracket.midpoint)
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
    """`BracketingSolver` is the base class for interval-reducing solvers; a subclass implements one `_step`.

    The base class implements the loop and the stopping criterion (`Interval.is_converged`), so
    a subclass cannot define a wrong one; one `_step` is one iteration. A solver that carries
    values between steps keeps them on its `SolveState` subclass (see `Solver.state_cls`).
    """

    def _solve(self, state: StateT) -> float:
        """Reduce the bracket with `_step` until `Interval.is_converged` holds; return `Interval.root`."""
        interval = state.bracket
        xtol_doubled = 2.0 * state.xtol
        while not interval.is_converged(xtol_doubled):
            interval = self._step(state, interval)
            state.x_best = interval.midpoint  # Cached on the interval: free when the step already used it.
        return interval.root()

    @abstractmethod
    def _step(self, state: StateT, interval: Interval) -> Interval:
        """Perform one iteration and return a strictly narrower bracket.

        Evaluate the function only through ``state.f``, and derive the new bracket
        with `Interval.split_at`, so the sign-change invariant is kept.
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
