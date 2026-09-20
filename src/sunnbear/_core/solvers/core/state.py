"""`SolverState` is the state of one solve, and the base class of a solver's own state."""

from dataclasses import dataclass

from .interval import Interval
from .wrapped_function import WrappedFunction


@dataclass
class SolverState:
    """A `SolverState` is the mutable state of one solve, created by `Solver.solve` and handed to `Solver._solve`.

    The fields below belong to `SolverState` itself, not to a solver's own subclass: `Solver.solve`
    fills them in and reads `n_iters` and `x_best` back into the result.

    A solver that carries values between iterations subclasses `SolverState`, adds its fields with
    defaults, and names the subclass in `Solver.state_cls`; `Solver.solve` instantiates whichever
    class is named there, so the solver never constructs a state itself.

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
