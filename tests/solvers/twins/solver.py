"""This module holds `TwinSolver`, the base class of every twin, and the function wrapper that stops a twin."""

from abc import abstractmethod
from typing import ClassVar

from sunnbear.solvers import Interval, Solver, SolveResult, SolveState


class TwinSolver(Solver):
    """A `TwinSolver` is a test-only `Solver` that runs a reference implementation, and declares how it deviates
    from exact agreement.

    A subclass implements `_run_reference`; `_solve` wraps the function in a `TwinFunction`, so that every twin
    stops where sunnbear's solver would stop. Where that solver has a stopping criterion of its own, not
    `BracketingSolver`'s, the subclass also overrides `_root_if_stopped` with that criterion.

    Attributes:
        n_reevaluated_bounds: The number of evaluations that the reference implementation makes at the interval
            bounds before its first iterate, after the framework already evaluated them. The agreement check leaves
            them out of the twin's evaluations.
    """

    n_reevaluated_bounds: ClassVar[int] = 0

    def _solve(self, state: SolveState) -> float:
        """Run the reference implementation through a `TwinFunction`, which stops it where sunnbear's solver would."""
        f = TwinFunction(state, self)
        try:
            self._run_reference(f, float(state.interval.a), float(state.interval.b), float(state.xtol))
        except TwinConvergedSignal as converged:
            return converged.x
        raise AssertionError("The reference implementation stopped before sunnbear's stopping criterion held.")

    @abstractmethod
    def _run_reference(self, f: "StoppingWrappedFunction", a: float, b: float, xtol: float) -> None:
        """Run the reference implementation on ``f`` over ``[a, b]``."""

    def _root_if_stopped(self, interval: Interval, evaluations: list[tuple[float, float]], xtol: float) -> float | None:
        """Return the root estimate if sunnbear's solver stops after ``evaluations``, or ``None`` if it continues.

        ``evaluations`` holds every ``(x, f(x))`` that the reference implementation evaluated, in order, without the
        evaluations at the interval bounds; ``interval`` is the initial interval split at each of those x-values. Both
        hold plain floats. This default is the stopping criterion of `BracketingSolver`, `Interval.is_converged`.
        """
        if interval.is_converged(2.0 * xtol):
            return interval.root()
        else:
            return None

    def history_without_reevaluations(self, result: SolveResult) -> list[tuple[float, float]]:
        """Return ``result.history`` without the reference implementation's re-evaluations of the interval bounds.

        The re-evaluations follow the framework's 2 evaluations at the interval bounds.
        """
        history = list(result.history)
        del history[2 : 2 + self.n_reevaluated_bounds]
        return history


class TwinConvergedSignal(Exception):  # noqa: N818 — the name marks a control-flow signal, not an error condition.
    """`TwinConvergedSignal` ends a reference implementation's loop once sunnbear's stopping criterion holds.

    Attributes:
        x: The root estimate that sunnbear's solver would report at that point, from `TwinSolver._root_if_stopped`.
    """

    def __init__(self, x: float) -> None:
        """Hold the root estimate."""
        super().__init__(x)
        self.x = x


class StoppingWrappedFunction:
    """A `StoppingWrappedFunction` is the function being solved, wrapped for a twin's reference implementation.

    Each call evaluates through the solve's ``state.f``, the framework's own `WrappedFunction`, so the evaluation is
    counted, capped and recorded in the history.

    Each call also splits a plain-float copy of the interval at the evaluated point, and raises
    `TwinConvergedSignal` once the twin's `TwinSolver._root_if_stopped` returns a root estimate. The copy holds plain
    floats, so the twin's bookkeeping adds no counted flops.

    The first ``n_reevaluated_bounds`` calls, the reference implementation's own evaluations of the interval
    bounds, do not split the interval.
    """

    def __init__(self, state: SolveState, twin: TwinSolver) -> None:
        """Start from the solve's initial interval."""
        interval = state.interval
        self._f = state.f
        self._twin = twin
        self._interval = Interval.from_interval_bounds(
            float(interval.a), float(interval.b), float(interval.fa), float(interval.fb)
        )
        self._xtol = float(state.xtol)
        self._evaluations: list[tuple[float, float]] = []
        self._n_reevaluated_bounds_left = twin.n_reevaluated_bounds

    def __call__(self, x: float) -> float:
        """Return ``f(x)``, or raise `TwinConvergedSignal` if sunnbear's solver would stop after this evaluation."""
        fx = float(self._f(x))
        if self._n_reevaluated_bounds_left > 0:
            self._n_reevaluated_bounds_left -= 1
        else:
            self._interval = self._interval.split_at(float(x), fx)
            self._evaluations.append((float(x), fx))
            x_root = self._twin._root_if_stopped(self._interval, self._evaluations, self._xtol)
            if x_root is not None:
                raise TwinConvergedSignal(x_root)
        return fx
