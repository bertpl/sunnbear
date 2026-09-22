"""`SolverState` is the state of one solve, and the base class of a solver's own state."""

from dataclasses import dataclass

from .interval import Interval
from .wrapped_function import WrappedFunction


@dataclass
class SolverState:
    """A `SolverState` is the mutable state of one solve, created by `Solver.solve` and handed to `Solver._solve`.

    The fields below belong to `SolverState` itself, not to a solver's own subclass. At the start of a
    solve, `Solver.solve` initializes `f`, `bracket`, `xtol`, and `x_best` (the bracket's midpoint); at
    the end, it copies `n_iters` and `x_best` into the `SolveResult`.

    A solver that needs additional fields in its state subclasses `SolverState`, adds its fields with
    defaults, and names the subclass in `Solver.state_cls`; `Solver.solve` instantiates whichever
    class is named there, so the solver never constructs a state itself.

    Attributes:
        f: The wrapped function to evaluate.
        bracket: The initial bracket ``[a, b]``; its class says whether it is increasing or decreasing, see `Interval`.
        xtol: Requested x-tolerance, ``|x_true - x| <= xtol``, as a `CountedFloat` so arithmetic on it is counted.
        n_iters: Iterations performed so far; ``None`` unless the solver counts
            iterations.
        x_best: Best root estimate so far; reported as the solve's final ``x`` when
            the solve ends early, so a solver keeps it current.
    """

    f: WrappedFunction
    bracket: Interval
    xtol: float
    n_iters: int | None = None
    x_best: float = 0.0

    def incr_iteration_count(self) -> None:
        """Count one iteration; the first call turns iteration counting on."""
        self.n_iters = 1 if self.n_iters is None else self.n_iters + 1
