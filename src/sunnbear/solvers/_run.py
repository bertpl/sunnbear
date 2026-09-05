"""The per-solve context a solver implementation works with."""

from dataclasses import dataclass

from ._wrapped_function import WrappedFunction


@dataclass
class SolveRun:
    """Mutable state of one solve, handed to `Solver._solve` and `BracketingSolver._step`.

    This is the only mutable object in the solver layer: solver instances stay
    immutable configuration, so one instance can serve any number of solves.

    Attributes:
        f: The wrapped function to evaluate; its values are sign-normalized so
            that ``f(a) <= 0 <= f(b)``.
        a: Lower end of the initial bracket, as a `CountedFloat`.
        b: Upper end of the initial bracket, as a `CountedFloat`.
        fa: ``f(a)`` after normalization, as a `CountedFloat`.
        fb: ``f(b)`` after normalization, as a `CountedFloat`.
        xtol: Requested x-tolerance.
        n_iters: Iterations performed so far; ``None`` until a solver declares
            that it counts them (see `mark_iteration`).
        x_best: Best root estimate so far. Reported as the result's ``x`` when
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
