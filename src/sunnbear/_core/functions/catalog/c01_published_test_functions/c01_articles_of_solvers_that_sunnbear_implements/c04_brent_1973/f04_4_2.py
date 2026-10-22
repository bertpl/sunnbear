"""This module holds the formula of (4.2) in Brent (1973).

The survey describes this function in words, not as 1 expression, so a person writes this module: a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Brent197342(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source describes ``fl(exp(x))`` if ``x > -10^6``; ``fl(exp(-10^6) - (x + 10^6)^2)`` otherwise; the formula's
    interval is ``[-1001200, 0]``, with ``t = 1E-20``.

    ``fl(.)`` as in (4.1): the computed floating-point value. In float64, ``exp(-10^6)`` is 0.
    """

    number = (1, 1, 4, 4)
    name = "(4.2)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall, "
            "Englewood Cliffs, NJ. ISBN 0-13-022335-2. Author's scan: "
            "https://maths-people.anu.edu.au/~brent/pub/pub011.html. Erratum: Brent, R. P. (1975). "
            "Table Errata 520. Mathematics of Computation, p. 1166."
        ),
        location="(4.2)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1001200.0 * c
        if x > -1e6:
            return math.exp(x)
        else:
            return math.exp(-1e6) - (x + 1e6) ** 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1001200.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-700840.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={}, x=-700840.0, c=0.25, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1001200.0, 0.0)),
    )
