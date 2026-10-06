"""This module declares `ITPState`, the state that `ITP` carries between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import SolveState


@dataclass
class ITPState(SolveState):
    """`ITPState` adds the values of the ITP method that `ITP` sets at the start of a solve and uses in every iteration.

    Attributes:
        kappa_1: The paper's truncation constant ``kappa_1``, which `ITP._solve` sets from the width of the initial
            interval.
        max_next_width: ``xtol * 2^(n_max - k)`` before iteration ``k``, with ``n_max`` the iteration bound that the
            `ITP` docstring defines: the largest width that the interval may have after that iteration, so that the
            solve still ends within ``n_max`` iterations. `ITP` halves it every iteration.
    """

    kappa_1: float = field(init=False)
    max_next_width: float = field(init=False)
