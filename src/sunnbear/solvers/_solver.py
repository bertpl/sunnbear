"""Solver base classes: the measurement-owning template method and the bracketing loop.

`Solver.solve` owns everything measurement-related — wrapping, flop-counting
contexts, initial bracket evaluations, sign normalization, exception-to-status
mapping, result packaging — so a concrete solver contributes pure algorithm
code. `BracketingSolver` additionally owns the reduction loop, its stopping
criteria, and root extraction: subclasses implement a single interval-reduction
step, which makes a wrong stopping criterion (a classic root-solver defect)
impossible to introduce in a subclass and yields an honest, uniform iteration
count. A solver whose published form deliberately deviates can still override
``_solve`` directly.

Solver-specific configuration goes through ``__init__`` only; ``solve(...)``
has the same signature for every solver.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Generic, TypeVar, cast

from counted_float import CountedFloat, FlopCountingContext

from sunnbear.errors import DivergedError, FunctionDomainError, MaxFevalsExceeded, SolveInterrupt
from sunnbear.functions import XFun

from ._interval import Interval
from ._result import SolveResult, SolveStatus
from ._run import SolveRun
from ._wrapped_function import WrappedFunction

_INTERRUPT_STATUS: dict[type[SolveInterrupt], SolveStatus] = {
    MaxFevalsExceeded: SolveStatus.MAX_FEVALS,
    DivergedError: SolveStatus.DIVERGED,
    FunctionDomainError: SolveStatus.FUNCTION_ERROR,
}


# ==================================================================================================
#  Solver
# ==================================================================================================
class Solver(ABC):
    """Base class for benchmarkable root solvers; see the module docstring for the contract."""

    name: ClassVar[str]
    version: ClassVar[int]

    # --------------------------------------------------------------------------
    #  Template method
    # --------------------------------------------------------------------------
    def solve(
        self,
        f: XFun,
        a: float,
        b: float,
        *,
        xtol: float,
        max_fevals: int,
        record_history: bool = False,
    ) -> SolveResult:
        """Find a root of `f` in the bracket ``[a, b]``.

        Args:
            f: The function to solve; ``f(a) * f(b) < 0`` is required.
            a: Lower bracket endpoint.
            b: Upper bracket endpoint.
            xtol: X-tolerance: the solution satisfies ``|x_true - x| <= xtol``.
            max_fevals: Function-evaluation budget; exceeding it terminates the
                run with status ``MAX_FEVALS``.
            record_history: Record all ``(x, f(x))`` evaluations in the result.

        Returns:
            The solve outcome; abnormal terminations are reported via
            ``status``, never raised.

        Raises:
            ValueError: If the bracket or tolerances are malformed, or
                ``f(a)`` and ``f(b)`` have the same (nonzero) sign.
        """
        # --- validate ------------------------------
        if not a < b:
            raise ValueError(f"solve requires a < b (got [{a}, {b}]).")
        if xtol <= 0.0:
            raise ValueError(f"solve requires xtol > 0 (got {xtol}).")
        if max_fevals < 2:
            raise ValueError(f"solve requires max_fevals >= 2 (got {max_fevals}).")

        # --- run, inside counting context ----------
        wf = WrappedFunction(f, a, b, max_fevals, record_history=record_history)
        run: SolveRun | None = None
        status = SolveStatus.CONVERGED
        x: float | None = None
        with FlopCountingContext() as ctx:
            try:
                run, x = self._initialize(wf, a, b, xtol)
            except SolveInterrupt as interrupt:
                status = _INTERRUPT_STATUS[type(interrupt)]
            else:
                # ValueError from _initialize (same-sign bracket: a caller bug) propagates above;
                # only algorithm-phase exceptions map to SOLVER_ERROR.
                if x is None:
                    try:
                        x = float(self._solve(run))
                    except SolveInterrupt as interrupt:
                        status = _INTERRUPT_STATUS[type(interrupt)]
                    except Exception:  # noqa: BLE001 — a solver bug becomes a status, not a batch abort
                        status = SolveStatus.SOLVER_ERROR

        # --- package -------------------------------
        if x is None:
            x = run.best_x if run is not None else (a + b) / 2.0
        return SolveResult(
            x=float(x),
            status=status,
            n_fevals=wf.n_fevals,
            n_iters=run.n_iters if run is not None else None,
            flop_counts=ctx.flop_counts(),
            history=tuple(wf.history) if wf.history is not None else None,
        )

    def _initialize(self, wf: WrappedFunction, a: float, b: float, xtol: float) -> tuple[SolveRun, float | None]:
        """Evaluate the bracket endpoints, normalize the sign, and build the run.

        Returns the run plus an immediate solution when an endpoint is an
        exact zero (in which case no solver code needs to execute).

        Raises:
            ValueError: If ``f(a)`` and ``f(b)`` have the same nonzero sign.
        """
        ca, cb = CountedFloat(a), CountedFloat(b)
        fa, fb = wf(ca), wf(cb)
        if fa * fb > 0.0:
            raise ValueError(f"solve requires f(a) * f(b) <= 0 (got f(a)={fa}, f(b)={fb}).")
        if fa > 0.0:
            wf.enable_negation()
            fa, fb = -fa, -fb
        run = SolveRun(f=wf, a=ca, b=cb, fa=fa, fb=fb, xtol=xtol, best_x=(a + b) / 2.0)
        if fa == 0.0:
            return run, a
        if fb == 0.0:
            return run, b
        return run, None

    # --------------------------------------------------------------------------
    #  Subclass hook
    # --------------------------------------------------------------------------
    @abstractmethod
    def _solve(self, run: SolveRun) -> float:
        """Run the algorithm and return the root estimate.

        The bracket is sign-normalized (``run.fa <= 0 <= run.fb``); all
        evaluations must go through ``run.f``. Update ``run.best_x`` as
        estimates improve and call ``run.mark_iteration()`` per iteration
        where the notion applies.
        """


# ==================================================================================================
#  BracketingSolver
# ==================================================================================================
S = TypeVar("S")


@dataclass(frozen=True)
class StepOutcome(Generic[S]):
    """Result of one bracketing step: the reduced interval plus carried solver state."""

    interval: Interval
    state: S


class BracketingSolver(Solver, Generic[S]):
    """Base class for interval-reducing solvers; subclasses implement one `_step`.

    The base loop owns the stopping criteria — interval narrow enough
    (``width <= 2 * xtol``, root = midpoint) or an endpoint exactly zero
    (root = that endpoint) — and the iteration count (one `_step` = one
    iteration). Type parameter `S` is the solver's per-run carried state;
    memoryless solvers use ``None``.
    """

    def _solve(self, run: SolveRun) -> float:
        """Run the reduction loop until a stopping criterion is met."""
        interval = Interval(a=run.a, b=run.b, fa=run.fa, fb=run.fb)
        state = self._initial_state(run, interval)
        while True:
            if interval.fa == 0.0:
                return interval.a
            if interval.fb == 0.0:
                return interval.b
            if interval.width <= 2.0 * run.xtol:
                return interval.midpoint
            outcome = self._step(run, interval, state)
            interval, state = outcome.interval, outcome.state
            run.mark_iteration()
            run.best_x = float(interval.midpoint)

    # --------------------------------------------------------------------------
    #  Subclass hooks
    # --------------------------------------------------------------------------
    def _initial_state(self, run: SolveRun, interval: Interval) -> S:
        """Build the solver's carried state for a fresh run (default: none)."""
        return cast(S, None)

    @abstractmethod
    def _step(self, run: SolveRun, interval: Interval, state: S) -> StepOutcome[S]:
        """Reduce the interval by one iteration, evaluating through ``run.f``."""
