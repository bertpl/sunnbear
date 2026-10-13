"""This module declares `ITPState`, the state that `ITP` carries between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import SolveState


@dataclass
class ITPState(SolveState):
    """`ITPState` adds the values of the ITP method that `ITP` sets at the start of a solve and uses in every iteration.

    Attributes:
        kappa_1: The paper's truncation constant ``kappa_1``, which `ITP._solve` sets from the width of the initial
            interval.
        n_max: The iteration bound ``n_max = n_bisection + n_slack`` that the `ITP` docstring defines, which
            `ITP._solve` sets from the initial interval.
        k: The number of the current iteration, counted from 0, which `ITP._next_x` advances.
    """

    kappa_1: float = field(init=False)
    n_max: int = field(init=False)
    k: int = 0
