"""`Solver` with its template method, and `BracketingSolver`, are the solver base classes.

Everything that makes a solve measurable lives in `Solver.solve` and the
`WrappedFunction` it installs; a subclass writes only the algorithm.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import ClassVar, Generic

from counted_float import CountedFloat, FlopCountingContext
from typing_extensions import TypeVar

from .exceptions import DivergedError, FunctionDomainError, MaxFevalsExceeded
from .interval import Interval
from .result import SolveResult, SolveStatus
from .state import SolverState
from .wrapped_function import WrappedFunction

# The state type a solver works with; a solver with fields of its own binds it to its `SolverState` subclass.
StateT = TypeVar("StateT", bound=SolverState, default=SolverState)


# ==================================================================================================
#  Solver
# ==================================================================================================
class Solver(ABC, Generic[StateT]):
    """`Solver` is the base class every benchmarkable root solver subclasses.

    A subclass implements `_solve` and takes its configuration through
    ``__init__``; `solve` has a fixed signature, so all solvers are driven
    identically. Instances are immutable configuration, safe to share across
    solves: everything that changes during a solve lives in the `SolverState`
    that `solve` creates and hands to the algorithm.

    Class attributes:
        name: Canonical identifier fragment, e.g. ``"bisection"``; with
            `version` and the init arguments, the name identifies a solver in
            benchmark results.
        version: Bumped on any behavior change, so results from different
            versions of one solver are never combined unknowingly.
        state_cls: The `SolverState` class that `solve` instantiates. A solver
            that carries values between iterations names its own subclass here
            and binds ``StateT`` to it; a memoryless solver leaves both alone.
    """

    name: ClassVar[str]
    version: ClassVar[int]
    state_cls: ClassVar[type[SolverState]] = SolverState

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
        record_history: bool = False,
    ) -> SolveResult:
        """Find a root of ``f`` in ``[a, b]`` and report what the solve did.

        - The endpoints are evaluated first; an endpoint that is exactly zero
          ends the solve as ``CONVERGED`` without running the algorithm.
        - The sign is then normalized, so the algorithm is given ``f(a) <= 0 <= f(b)``.
        - Every abnormal ending becomes a `SolveStatus`, not an exception: one
          broken solver must not abort a batch of a million solves.

        Args:
            f: The function; must be finite on ``[a, b]`` and change sign across it.
            a: Lower end of the bracket, which also sizes the guard interval.
            b: Upper end of the bracket, which also sizes the guard interval.
            xtol: Requested x-tolerance, ``|x_true - x| <= xtol``.
            max_fevals: Function-evaluation budget, the two endpoint evaluations included.
            record_history: Whether to keep every ``(x, f(x))`` pair in the result.

        Raises:
            ValueError: If ``a >= b`` or ``f(a)`` and ``f(b)`` have the same sign — a
                caller error, not a solve outcome.
        """
        if not a < b:
            raise ValueError(f"Bracket must satisfy a < b (got a={a}, b={b}).")
        wrapped_f = WrappedFunction(f, a, b, max_fevals=max_fevals, record_history=record_history)
        with FlopCountingContext() as flop_ctx:
            fa_plain, fb_plain = float(wrapped_f(a)), float(wrapped_f(b))
            if fa_plain == 0.0 or fb_plain == 0.0:
                x, status, n_iters = (a if fa_plain == 0.0 else b), SolveStatus.CONVERGED, None
            else:
                if fa_plain * fb_plain > 0.0:
                    raise ValueError(f"f(a) and f(b) must differ in sign (got f({a})={fa_plain}, f({b})={fb_plain}).")
                if fa_plain > 0.0:
                    wrapped_f.enable_sign_normalization()
                    fa_plain, fb_plain = -fa_plain, -fb_plain
                bracket = Interval(CountedFloat(a), CountedFloat(b), CountedFloat(fa_plain), CountedFloat(fb_plain))
                state = self.state_cls(f=wrapped_f, bracket=bracket, xtol=xtol, x_best=_plain_midpoint(a, b))
                x, status = self._run_catching_exceptions(state)
                n_iters = state.n_iters
        return SolveResult(
            x=float(x),
            status=status,
            n_fevals=wrapped_f.n_fevals,
            n_iters=n_iters,
            flop_counts=flop_ctx.flop_counts(),
            history=None if wrapped_f.history is None else tuple(wrapped_f.history),
        )

    def _run_catching_exceptions(self, state: SolverState) -> tuple[float, SolveStatus]:
        """Run the algorithm and map how it ended to a root estimate and a status.

        The state is typed as the base class here because `state_cls` is declared as one; `_solve`
        receives the subclass instance it was created as.
        """
        try:
            return self._solve(state), SolveStatus.CONVERGED  # type: ignore[arg-type]
        except MaxFevalsExceeded:
            return state.x_best, SolveStatus.MAX_FEVALS
        except DivergedError:
            return state.x_best, SolveStatus.DIVERGED
        except FunctionDomainError:
            return state.x_best, SolveStatus.FUNCTION_ERROR
        except Exception:  # noqa: BLE001 — a solver bug becomes a recorded status, by design
            return state.x_best, SolveStatus.SOLVER_ERROR

    # --------------------------------------------------------------------------
    #  Subclass hook
    # --------------------------------------------------------------------------
    @abstractmethod
    def _solve(self, state: StateT) -> float:
        """Run the algorithm on `state` and return the root estimate.

        - Evaluate the function only through ``state.f``, and let its interrupts propagate.
        - Keep ``state.x_best`` current, so an interrupted solve still reports a meaningful ``x``.
        - Call ``state.mark_iteration()`` once per iteration, if the algorithm has iterations.
        """


# ==================================================================================================
#  BracketingSolver
# ==================================================================================================
class BracketingSolver(Solver[StateT]):
    """`BracketingSolver` is the base class for interval-reducing solvers; a subclass implements one `_step`.

    The base class implements the loop and the stopping criterion (`Interval.is_converged`), so
    a subclass cannot define a wrong one; one `_step` is one iteration. A solver that carries
    values between steps keeps them on its `SolverState` subclass (see `Solver.state_cls`).
    """

    def _solve(self, state: StateT) -> float:
        """Reduce the bracket with `_step` until `Interval.is_converged` holds; return `Interval.root`."""
        interval = state.bracket
        xtol_doubled = 2.0 * state.xtol
        state.n_iters = 0
        while not interval.is_converged(xtol_doubled):
            interval = self._step(state, interval)
            state.mark_iteration()
            state.x_best = _plain_midpoint(float(interval.a), float(interval.b))
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
def _plain_midpoint(a: float, b: float) -> float:
    """Return the midpoint of two plain floats; bookkeeping, so not counted as solver cost."""
    return 0.5 * (a + b)
