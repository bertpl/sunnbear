"""The solver base classes: `Solver` with its template method, and `BracketingSolver`.

A third-party solver subclasses one of the two and implements a single hook.
Everything that makes a solve measurable — evaluation counting, the budget,
the guards, flop counting, sign normalization, stopping criteria, result
packaging — lives here, so a solver author writes straight-line algorithm code
and cannot get the measurement wrong.
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
    """Base class for every benchmarkable root solver.

    Subclasses implement `_solve` and may add configuration through their
    ``__init__``; `solve` itself has a fixed signature, so all solvers are
    driven identically. Instances are immutable configuration and can be
    shared freely across solves.

    Class attributes:
        name: Canonical identifier fragment (e.g. ``"bisection"``); together
            with `version` and the init arguments it identifies a solver in
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

        The two endpoint evaluations happen here and count toward `n_fevals`.
        An endpoint that is exactly zero ends the solve as ``CONVERGED`` without
        involving the algorithm. Afterwards the sign is normalized so the
        algorithm sees ``f(a) <= 0 <= f(b)``, and every abnormal termination is
        mapped to a `SolveStatus` instead of propagating: one broken solver
        must not abort a batch of a million solves.

        Args:
            f: The function; must be finite on ``[a, b]`` and change sign across it.
            a: Lower end of the bracket.
            b: Upper end of the bracket.
            xtol: Requested x-tolerance: ``|x_true - x| <= xtol``.
            max_fevals: Function-evaluation budget, the endpoint evaluations included.
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
                run = SolveRun(
                    f=wf,
                    a=CountedFloat(a),
                    b=CountedFloat(b),
                    fa=CountedFloat(fa_plain),
                    fb=CountedFloat(fb_plain),
                    xtol=xtol,
                    x_best=0.5 * (a + b),
                )
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
        """Run the algorithm and map how it ended to a root estimate and status."""
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

        Evaluate the function only through ``run.f``; let its interrupts
        propagate. Keep ``run.x_best`` current so an interrupted solve still
        reports a meaningful ``x``, and call ``run.mark_iteration()`` per
        iteration if the algorithm has iterations.
        """


# ==================================================================================================
#  BracketingSolver
# ==================================================================================================
S = TypeVar("S")


class BracketingSolver(Solver, Generic[S]):
    """Base class for interval-reducing solvers; subclasses implement one `_step`.

    The base owns the loop, the stopping criteria, the root extraction, and the
    iteration count, so a subclass cannot ship a subtly wrong stopping rule and
    every bracketing solver counts iterations the same way: one `_step` is one
    iteration. A solver that carries state between steps declares it as the
    type parameter ``S`` and threads it through `_step`; memoryless solvers use
    ``S = None``.

    Stopping criteria, checked before every step:

    - **[A]** the bracket width is at most ``2 * xtol`` — the root estimate is
      the midpoint, within ``xtol`` of the true root;
    - **[B]** an endpoint value is exactly zero — that endpoint is the root.
    """

    def _solve(self, run: SolveRun) -> float:
        """Reduce the bracket with `_step` until a stopping criterion holds; return the root estimate."""
        interval = Interval(run.a, run.b, run.fa, run.fb)
        state = self._initial_state(run, interval)
        two_xtol = 2.0 * run.xtol
        run.n_iters = 0
        while not interval.is_converged(two_xtol):
            interval, state = self._step(run, interval, state)
            run.mark_iteration()
            run.x_best = 0.5 * (float(interval.a) + float(interval.b))  # plain floats: bookkeeping, not solver cost
        return interval.root()

    def _initial_state(self, run: SolveRun, interval: Interval) -> S:
        """Return the state carried into the first `_step`.

        Default: ``None``, for memoryless solvers (``S = None``). A stateful
        solver overrides this; the cast is what lets one default serve every
        ``S`` without forcing memoryless solvers to write it out.
        """
        return cast("S", None)

    @abstractmethod
    def _step(self, run: SolveRun, interval: Interval, state: S) -> tuple[Interval, S]:
        """Perform one iteration: return a strictly narrower bracket and the state for the next step.

        Evaluate the function only through ``run.f``, and derive the new bracket
        with `Interval.replace` so the sign-change invariant is kept.
        """
