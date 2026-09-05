"""`Solver` with its template method, and `BracketingSolver`, are the base classes a solver subclasses.

Everything that makes a solve measurable lives in `Solver.solve` and the
`WrappedFunction` it installs; a subclass writes only the algorithm.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import ClassVar, Generic, TypeVar, cast

from counted_float import CountedFloat, FlopCountingContext

from sunnbear.errors import DivergedError, FunctionDomainError, MaxFevalsExceeded

from ._interval import Interval
from ._result import SolveResult, SolveStatus
from ._run import SolveRun
from ._wrapped_function import WrappedFunction


# ==================================================================================================
#  Solver
# ==================================================================================================
class Solver(ABC):
    """`Solver` is the base class every benchmarkable root solver subclasses.

    A subclass implements `_solve` and takes its configuration through
    ``__init__``; `solve` has a fixed signature, so all solvers are driven
    identically. Instances are immutable configuration, safe to share across
    solves.

    Class attributes:
        name: Canonical identifier fragment, e.g. ``"bisection"``; with
            `version` and the init arguments, the name identifies a solver in
            benchmark results.
        version: Bumped on any behavior change, so results from different
            versions of one solver are never pooled unknowingly.
    """

    name: ClassVar[str]
    version: ClassVar[int]

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
        - The sign is then normalized, so the algorithm sees ``f(a) <= 0 <= f(b)``.
        - Every abnormal ending becomes a `SolveStatus`, not an exception: one
          broken solver must not abort a batch of a million solves.

        Args:
            f: The function; must be finite on ``[a, b]`` and change sign across it.
            a: Lower end of the bracket, which also sizes the divergence guard.
            b: Upper end of the bracket.
            xtol: Requested x-tolerance, ``|x_true - x| <= xtol``.
            max_fevals: Function-evaluation budget, the two endpoint evaluations included.
            record_history: Whether to keep every ``(x, f(x))`` pair in the result.

        Raises:
            ValueError: If ``a >= b`` or ``f(a)`` and ``f(b)`` have the same sign — a
                caller error, not a solve outcome.
        """
        if not a < b:
            raise ValueError(f"Bracket must satisfy a < b (got a={a}, b={b}).")
        wf = WrappedFunction(f, a, b, max_fevals=max_fevals, record_history=record_history)
        with FlopCountingContext() as ctx:
            fa_plain, fb_plain = float(wf(a)), float(wf(b))
            if fa_plain == 0.0 or fb_plain == 0.0:
                x, status, n_iters = (a if fa_plain == 0.0 else b), SolveStatus.CONVERGED, None
            else:
                if fa_plain * fb_plain > 0.0:
                    raise ValueError(f"f(a) and f(b) must differ in sign (got f({a})={fa_plain}, f({b})={fb_plain}).")
                if fa_plain > 0.0:
                    wf.enable_sign_normalization()
                    fa_plain, fb_plain = -fa_plain, -fb_plain
                bracket = Interval(CountedFloat(a), CountedFloat(b), CountedFloat(fa_plain), CountedFloat(fb_plain))
                run = SolveRun(f=wf, bracket=bracket, xtol=xtol, x_best=0.5 * (a + b))
                x, status = self._run_guarded(run)
                n_iters = run.n_iters
        return SolveResult(
            x=float(x),
            status=status,
            n_fevals=wf.n_fevals,
            n_iters=n_iters,
            flop_counts=ctx.flop_counts(),
            history=None if wf.history is None else tuple(wf.history),
        )

    def _run_guarded(self, run: SolveRun) -> tuple[float, SolveStatus]:
        """Run the algorithm and map how it ended to a root estimate and a status."""
        try:
            return self._solve(run), SolveStatus.CONVERGED
        except MaxFevalsExceeded:
            return run.x_best, SolveStatus.MAX_FEVALS
        except DivergedError:
            return run.x_best, SolveStatus.DIVERGED
        except FunctionDomainError:
            return run.x_best, SolveStatus.FUNCTION_ERROR
        except Exception:  # noqa: BLE001 — a solver bug becomes a recorded status, by design
            return run.x_best, SolveStatus.SOLVER_ERROR

    # --------------------------------------------------------------------------
    #  Subclass hook
    # --------------------------------------------------------------------------
    @abstractmethod
    def _solve(self, run: SolveRun) -> float:
        """Run the algorithm on `run` and return the root estimate.

        - Evaluate the function only through ``run.f``, and let its interrupts propagate.
        - Keep ``run.x_best`` current, so an interrupted solve still reports a meaningful ``x``.
        - Call ``run.mark_iteration()`` once per iteration, if the algorithm has iterations.
        """


# ==================================================================================================
#  BracketingSolver
# ==================================================================================================
S = TypeVar("S")


class BracketingSolver(Solver, Generic[S]):
    """`BracketingSolver` is the base class for interval-reducing solvers; a subclass implements one `_step`.

    The base owns the loop and the stopping rule (`Interval.is_converged`), so
    a subclass cannot define a wrong one; one `_step` is one iteration. A
    solver that carries state between steps declares its type as ``S`` and
    threads it through `_step`; memoryless solvers use ``S = None``.
    """

    def _solve(self, run: SolveRun) -> float:
        """Reduce the bracket with `_step` until `Interval.is_converged` holds; return `Interval.root`."""
        interval = run.bracket
        state = self._initial_state(run, interval)
        two_xtol = 2.0 * run.xtol
        run.n_iters = 0
        while not interval.is_converged(two_xtol):
            interval, state = self._step(run, interval, state)
            run.mark_iteration()
            # Plain floats, so this bookkeeping is not counted as solver cost.
            run.x_best = 0.5 * (float(interval.a) + float(interval.b))
        return interval.root()

    def _initial_state(self, run: SolveRun, interval: Interval) -> S:
        """Return the state carried into the first `_step`; ``None`` by default, for memoryless solvers.

        The cast lets one default serve every ``S``.
        """
        return cast("S", None)

    @abstractmethod
    def _step(self, run: SolveRun, interval: Interval, state: S) -> tuple[Interval, S]:
        """Perform one iteration: return a strictly narrower bracket and the state for the next step.

        Evaluate the function only through ``run.f``, and derive the new bracket
        with `Interval.replace`, so the sign-change invariant is kept.
        """
