"""This module holds the formula that Dowell, Jarratt (1972) labels Problem 3.

The survey gives this function as an infinite sum, an expression that the script does not translate, so a person writes
this module: a change of the formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class DowellJarratt1972Problem3(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``sum((-1)^n*x^((3*n^2 + n)/2), n = -inf..inf) - 1``; the formula's
    interval is ``[-0.9999, -0.0001]``.

    The formula sums the terms of ``n`` and ``-n`` together, from ``n = 1`` up, until adding them no longer changes the
    sum in float64, which happens for every x in ``(-1, 1)``; outside ``(-1, 1)``, where the series diverges, the
    formula is NaN.

    Defined for ``-1 < x < 1``. Root ``-0.679334``. Starting values ``x0 = -0.0001``, ``x1 = -0.9999``. The article
    calls it a well-behaved function.
    """

    number = (1, 1, 2, 4)
    name = "Problem 3"
    param_names = ()
    source = FormulaSource(
        reference=(
            'Dowell, M., Jarratt, P. (1972). The "Pegasus" method for computing the root of an '
            "equation. BIT 12(4), 503–508. https://doi.org/10.1007/BF01932959."
        ),
        location="Problem 3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 0.9998 * c
        if not -1.0 < x < 1.0:
            # the series diverges outside (-1, 1)
            return math.nan
        else:
            # the term of n = 0 is 1; then the terms of n and -n, from n = 1 up, until adding them no longer
            # changes the sum
            total = 1.0
            n = 1
            while True:
                term = (-1.0) ** n * (x ** ((3 * n * n - n) // 2) + x ** ((3 * n * n + n) // 2))
                if total + term == total:
                    return total - 1.0
                total += term
                n += 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.9999, -0.0001)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-0.69996, c=0.0, expected=-0.04892829857040081),
        FormulaTestCase.value(params={}, x=-0.69996, c=0.25, expected=-0.9973780415610394),
        FormulaTestCase.value(params={}, x=-0.9999, c=0.25, expected=math.nan),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.9999, -0.0001)),
    )
