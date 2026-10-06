"""`Ridders` implements Ridders' method: each iteration evaluates the midpoint, then a point from an exponential fit."""

import math
from typing import Literal

from sunnbear._core.solvers.core import Solver, SolveState


class Ridders(Solver):
    """`Ridders` implements Ridders' method (Ridders, IEEE Trans. Circuits and Systems 26, 1979).

    Each iteration evaluates the function twice, on the interval ``[x0, x2]``, with ``fi = f(xi)``:

    - at its midpoint ``x1``;
    - at the iterate ``x3 = x1 + d * (f1 / f0) / sqrt((f1 / f0)^2 - f2 / f0)``, with ``d = x1 - x0``. Each value
      ``fi`` is scaled by ``exp(m * xi)``, with ``m`` chosen so that the 3 scaled values lie on a straight line, and
      ``x3`` is where that line crosses 0. The formula for ``x3`` is the paper's final form of the step, its
      equation 6.

    ``x3`` always lies in the half of the interval that holds the sign change, so the next interval is the current
    interval, split first at ``x1`` and then at ``x3``.

    The paper leaves the stopping criterion open, so ``stopping_criterion`` chooses 1 of 2:

    - ``"original"`` stops when 2 successive iterates lie at most ``xtol`` apart, and returns the last one. On a
      function that is not smooth, the returned iterate can lie more than ``xtol`` from the true root.
    - ``"corrected"`` stops when the interval is at most ``2 * xtol`` wide, and returns its midpoint, so its root
      always lies within ``xtol`` of the true root.

    Under both, the solve stops as soon as an evaluation returns exactly 0, and returns that x-value.

    An iteration evaluates the function twice, so `Ridders` writes its own loop, not `BracketingSolver`'s.
    """

    name = "ridders"
    version = 1

    def __init__(self, *, stopping_criterion: Literal["original", "corrected"]) -> None:
        """Configure the stopping criterion.

        ``"original"`` stops once 2 successive iterates lie at most ``xtol`` apart, ``"corrected"`` once the interval
        is at most ``2 * xtol`` wide.

        Raises:
            ValueError: If ``stopping_criterion`` is neither ``"original"`` nor ``"corrected"``.
        """
        if stopping_criterion not in ("original", "corrected"):
            raise ValueError(f"stopping_criterion must be 'original' or 'corrected' (got {stopping_criterion!r}).")
        self.stopping_criterion = stopping_criterion

    def _solve(self, state: SolveState) -> float:
        """Run Ridders' iterations and return the root estimate.

        Each iteration evaluates the midpoint ``x1`` and then the iterate ``x3``, and splits the interval at both. The
        solve ends at an evaluation that returns exactly 0, or once the configured stopping criterion holds.
        """
        interval = state.interval
        if self.stopping_criterion == "corrected":
            xtol_doubled = 2.0 * state.xtol
        x3_previous: float | None = None  # The original criterion compares each new x3 with this previous one.
        while True:
            # --- corrected stopping criterion ---
            # It is checked before each iteration, so that an interval that is narrow enough costs no evaluation.
            if self.stopping_criterion == "corrected" and interval.width <= xtol_doubled:
                return interval.midpoint

            # --- x1, the midpoint ---------------
            x1 = interval.midpoint
            f1 = state.f(x1)
            state.x_best = x1
            if f1 == 0.0:
                return x1

            # --- x3, the paper's equation 6 -----
            f1_over_f0 = f1 / interval.fa
            x3 = x1 + (x1 - interval.a) * f1_over_f0 / math.sqrt(f1_over_f0 * f1_over_f0 - interval.fb / interval.fa)
            f3 = state.f(x3)
            state.x_best = x3
            if f3 == 0.0:
                return x3
            interval = interval.split_at(x1, f1).split_at(x3, f3)

            # --- original stopping criterion ----
            # It is checked after each iteration, because it compares 2 successive iterates.
            if self.stopping_criterion == "original":
                if x3_previous is not None and abs(x3 - x3_previous) <= state.xtol:
                    return x3
                x3_previous = x3
