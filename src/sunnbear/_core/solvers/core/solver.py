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
from .state import SolverState
from .wrapped_function import WrappedFunction

# A solver with fields of its own binds StateT to its SolverState subclass; see `Solver.state_cls`.
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
            and binds ``StateT`` to it; a memoryless solver leaves ``state_cls`` and ``StateT`` at their defaults.
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
        - The bracket handed to the solver is an `IncreasingInterval` or a `DecreasingInterval`,
          whichever the endpoint values hold; a solver that supports one orientation only decides
          for itself what to do with the other.
        - Every abnormal ending becomes a `SolveStatus`, not an exception: one
          broken solver must not abort a batch of a million solves.
        - Divergence is judged by where things ended, not by how far an iterate strayed: a solve
          whose result lies outside ``[a, b]``, or whose function error happened outside
          ``[a, b]``, is ``DIVERGED``. Excursions that return are not penalized, and there is no
          bound to justify.
        - Only the bracket-order check is uncounted. Everything after it runs on `CountedFloat`
          and is counted: the endpoint checks, ``xtol``, the bookkeeping of the best estimate, the
          solver's arithmetic, and the divergence check. An early exit therefore reports the
          comparisons that produced it.

        Args:
            f: The function; must be finite on ``[a, b]``, with ``f(a)`` and ``f(b)`` of opposite sign or zero.
            a: Lower end of the bracket.
            b: Upper end of the bracket.
            xtol: Requested x-tolerance, ``|x_true - x| <= xtol``.
            max_fevals: Function-evaluation budget, the 2 endpoint evaluations included.
            record_history: Whether to keep every ``(x, f(x))`` pair in the result.

        Raises:
            ValueError: If ``a >= b``, or ``f(a)`` and ``f(b)`` have the same sign and neither is
                zero — a caller error, not a solve outcome.
        """
        # --- uncounted validation -------------------
        if not a < b:
            raise ValueError(f"Bracket must satisfy a < b (got a={a}, b={b}).")
        wrapped_f = WrappedFunction(f, max_fevals=max_fevals, record_history=record_history)
        with FlopCountingContext() as flop_ctx:
            # --- counted: endpoints and early exits -----
            a_counted, b_counted, xtol_counted = CountedFloat(a), CountedFloat(b), CountedFloat(xtol)
            fa, fb = wrapped_f(a_counted), wrapped_f(b_counted)
            if fa == 0.0:
                x, status, n_iters = a_counted, SolveStatus.CONVERGED, None
            elif fb == 0.0:
                x, status, n_iters = b_counted, SolveStatus.CONVERGED, None
            else:
                # --- counted: the solver run ------------
                bracket = Interval.from_endpoints(a_counted, b_counted, fa, fb)
                state = self.state_cls(f=wrapped_f, bracket=bracket, xtol=xtol_counted, x_best=bracket.midpoint)
                x, status = self._run_catching_exceptions(state, a_counted, b_counted)
                n_iters = state.n_iters
        return SolveResult(
            x=float(x),
            status=status,
            n_fevals=wrapped_f.n_fevals,
            n_iters=n_iters,
            flop_counts=flop_ctx.flop_counts(),
            history=None if wrapped_f.history is None else tuple(wrapped_f.history),
        )

    def _run_catching_exceptions(self, state: SolverState, a: float, b: float) -> tuple[float, SolveStatus]:
        """Run the algorithm and map how it ended to a root estimate and a status.

        The state is typed as the base class here because `state_cls` is declared as one; `_solve`
        receives the instance of `state_cls` that `solve` created. ``a`` and ``b`` are `CountedFloat`,
        so the divergence checks are counted.
        """
        try:
            x, status = self._solve(state), SolveStatus.CONVERGED  # type: ignore[arg-type]
        except MaxFevalsExceeded:
            x, status = state.x_best, SolveStatus.MAX_FEVALS
        except DivergedError:
            x, status = state.x_best, SolveStatus.DIVERGED
        except FunctionDomainError as exc:
            x = state.x_best
            status = SolveStatus.FUNCTION_ERROR if a <= exc.x <= b else SolveStatus.DIVERGED
        except Exception:  # noqa: BLE001 — a solver bug becomes a recorded status, by design
            return state.x_best, SolveStatus.SOLVER_ERROR
        # A result outside the bracket is divergence whatever the solver reported, CONVERGED included.
        if not a <= x <= b:
            status = SolveStatus.DIVERGED
        return x, status

    # --------------------------------------------------------------------------
    #  Subclass hook
    # --------------------------------------------------------------------------
    @abstractmethod
    def _solve(self, state: StateT) -> float:
        """Run the algorithm on `state` and return the root estimate.

        - Evaluate the function only through ``state.f``, and let its interrupts propagate.
        - Keep ``state.x_best`` current, so an interrupted solve still reports a meaningful ``x``.
        - Call ``state.incr_iteration_count()`` once per iteration, if the algorithm has iterations.
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
            state.incr_iteration_count()
            state.x_best = interval.midpoint  # Cached on the interval: free when the step already used it.
        return interval.root()

    @abstractmethod
    def _step(self, state: StateT, interval: Interval) -> Interval:
        """Perform one iteration and return a strictly narrower bracket.

        Evaluate the function only through ``state.f``, and derive the new bracket
        with `Interval.split_at`, so the sign-change invariant is kept.
        """
