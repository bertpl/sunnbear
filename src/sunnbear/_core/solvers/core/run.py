"""`SolveRun` is the per-solve context a solver implementation works with."""

from dataclasses import dataclass

from .interval import Interval
from .wrapped_function import WrappedFunction


@dataclass
class SolveRun:
    """A `SolveRun` is the mutable state of one solve, handed to `Solver._solve` and `BracketingSolver._step`.

    Attributes:
        f: The wrapped function to evaluate, sign-normalized by `Solver.solve`.
        bracket: The initial bracket, its endpoints already `CountedFloat` as documented on `Interval`.
        xtol: Requested x-tolerance, ``|x_true - x| <= xtol``.
        n_iters: Iterations performed so far; ``None`` unless the solver counts
            iterations.
        x_best: Best root estimate so far; reported as the solve's final ``x`` when
            the solve is interrupted, so a solver keeps it current.
    """

    f: WrappedFunction
    bracket: Interval
    xtol: float
    n_iters: int | None = None
    x_best: float = 0.0

    def mark_iteration(self) -> None:
        """Count one iteration; the first call turns iteration counting on."""
        self.n_iters = 1 if self.n_iters is None else self.n_iters + 1
