"""This module holds `BrentWithPaperStoppingCriterion`, which lets a test run Brent's procedure ``zero`` with its own
stopping criterion."""

from sunnbear.solvers import Brent


class BrentWithPaperStoppingCriterion(Brent):
    """`BrentWithPaperStoppingCriterion` is `Brent` with the stopping criterion of Brent's procedure ``zero``: the
    solve ends once ``|m| <= tol`` or ``f(b) = 0``, and returns ``b``.

    `Brent` sets the procedure's absolute tolerance ``t`` to ``xtol``, so a test passes a published ``t`` as ``xtol``.
    """

    @staticmethod
    def _root_if_converged(
        b: float, fb: float, c: float, fc: float, m: float, tol: float, xtol_doubled: float
    ) -> float | None:
        """Return ``b`` if ``|m| <= tol`` or ``f(b) = 0``, or ``None`` if the solve continues."""
        if abs(m) <= tol or fb == 0.0:
            return b
        else:
            return None
