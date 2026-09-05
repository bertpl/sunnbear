"""`SolveRun` is the per-solve context a solver implementation works with."""

from dataclasses import dataclass

from ._wrapped_function import WrappedFunction


@dataclass
class SolveRun:
    """The mutable state of one solve, handed to `Solver._solve` and `BracketingSolver._step`.

    Attributes:
        f: The wrapped function to evaluate, sign-normalized by `Solver.solve`.
        a: Lower end of the initial bracket. Like ``b``, ``fa`` and ``fb``, a
            `CountedFloat`, so arithmetic on it is counted.
        b: Upper end of the initial bracket.
        fa: ``f(a)``.
        fb: ``f(b)``.
        n_iters: Iterations performed so far; ``None`` until `mark_iteration`
            is first called.
        x_best: Best root estimate so far; reported as the result's ``x`` when
            the solve is interrupted, so a solver keeps it current.
    """

    f: WrappedFunction
    a: float
    b: float
    fa: float
    fb: float
    xtol: float
    n_iters: int | None = None
    x_best: float = 0.0

    def mark_iteration(self) -> None:
        """Count one iteration; the first call turns iteration counting on."""
        self.n_iters = 1 if self.n_iters is None else self.n_iters + 1
