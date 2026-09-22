"""`SolveState` is the state of one solve, and the base class of a solver's own state."""

from dataclasses import dataclass

from .interval import Interval
from .wrapped_function import WrappedFunction


@dataclass
class SolveState:
    """A `SolveState` is the mutable state of one solve, created by `Solver.solve` and handed to `Solver._solve`.

    The fields below belong to `SolveState` itself, not to a solver's own subclass. At the start of a
    solve, `Solver.solve` initializes `f`, `interval`, `xtol`, and `x_best` (the interval's midpoint); at
    the end, it copies `x_best` into the `SolveResult`.

    A solver that needs additional fields in its state subclasses `SolveState`, adds its fields with
    defaults, and names the subclass in `Solver.state_cls`; `Solver.solve` instantiates whichever
    class is named there, so the solver never constructs a state itself.

    Attributes:
        f: The wrapped function to evaluate.
        interval: The initial interval ``[a, b]``; its class says whether it is increasing or decreasing, see
            `Interval`.
        xtol: Requested x-tolerance, ``|x_true - x| <= xtol``, as a `CountedFloat` so arithmetic on it is counted.
        x_best: Best root estimate so far; reported as the solve's final ``x`` when
            the solve ends early, so a solver keeps it current.
    """

    f: WrappedFunction
    interval: Interval
    xtol: float
    x_best: float = 0.0
