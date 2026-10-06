"""This module declares `ITPState`, the state that `ITP` carries between iterations."""

from dataclasses import dataclass, field

from sunnbear._core.solvers.core import SolveState


@dataclass
class ITPState(SolveState):
    """`ITPState` adds the 2 values of the ITP method that `ITP` sets once per solve and reads every iteration.

    Attributes:
        kappa_1: The truncation constant ``kappa_1 = 0.2 / (b0 - a0)``, with ``a0`` and ``b0`` the bounds of the
            initial interval.
        max_next_width: ``xtol * 2^(n_max - k)`` before iteration ``k``, the largest width that the interval may
            have after that iteration, so that the solve still ends within ``n_max`` iterations. `ITP` halves it
            every iteration.
    """

    kappa_1: float = field(init=False)
    max_next_width: float = field(init=False)
