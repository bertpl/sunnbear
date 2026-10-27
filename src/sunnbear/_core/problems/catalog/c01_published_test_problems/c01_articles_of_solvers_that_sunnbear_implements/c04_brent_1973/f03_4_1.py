"""This module holds a formula of Brent (1973).

The formula comes from the row with the key ``(4.1)`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Brent197341(Formula):
    """This formula comes from Brent (1973).

    The survey writes the source's function as ``0`` if ``abs(x) < 3.8*10^-4``; ``fl(x*exp(-x^-2))`` otherwise. The
    source names it ``f_1``. The formula's interval is ``[-1.0, +4.0]``, on which the book's procedure ``zero2`` solves
    with the absolute tolerance ``t = 1E-20``.

    ``fl(.)`` is the computed floating-point value. Table 4.1's footnote: ``zero2`` returned ``2.17E-4``, where ``f_1 =
    0``.

    In float64, ``x*exp(-x^-2)`` underflows to 0 for ``abs(x)`` below about 0.0367, so the formula is 0 on about
    ``[-0.0367, 0.0367]``. The book's procedure ``zero2`` represents each function value as ``y*2^z`` and does not
    underflow, so its ``f_1`` is 0 only for ``abs(x) < 3.8*10^-4``.
    """

    number = (1, 1, 4, 3)
    name = "(4.1)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall, "
            "Englewood Cliffs, NJ. ISBN 0-13-022335-2. Author's scan: "
            "https://maths-people.anu.edu.au/~brent/pub/pub011.html. Erratum: Brent, R. P. (1975). "
            "Table Errata 520. Mathematics of Computation 29(132), 1166. "
            "https://doi.org/10.1090/s0025-5718-1975-0371062-9."
        ),
        location="(4.1)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        if abs(x) < 3.8e-4:
            return 0.0
        else:
            return x * math.exp(-(x**-2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(params={}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={}, x=0.0001, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 4.0)),
    )
