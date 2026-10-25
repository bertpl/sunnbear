"""This module holds a formula of Dowell, Jarratt (1972).

The formula comes from the row with the key ``Problem 3`` in the survey of published test problems. The survey gives
this function as 1 expression that the module generator, `scripts/literature_test_problems/formula_modules.py`, cannot
translate: an infinite sum.

Nor does the generator write a formula with the parameter ``modified``, which selects a modified version of a
published test problem. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class DowellJarratt1972Problem3(Formula):
    """This formula comes from Dowell, Jarratt (1972).

    The survey writes the source's function as ``sum((-1)^n*x^((3*n^2 + n)/2), n = -inf..inf) - 1``; the formula's
    interval is ``[-0.9999, -0.0001]``.

    The formula sums the terms of ``n`` and ``-n`` together, from ``n = 1`` up, until adding them no longer changes the
    sum in float64, which happens for every x in ``(-1, 1)``; outside ``(-1, 1)``, where the series diverges, the
    formula is NaN.

    Defined for ``-1 < x < 1``. Root ``-0.679334``. Starting values ``x0 = -0.0001``, ``x1 = -0.9999``. The article
    calls it a well-behaved function.

    With ``modified = 1``, the formula keeps the published interval, evaluates the published function at x without
    shifting x, and adds ``c`` to the function's value.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``b = -0.0001`` lies
    ``1e-4`` from a second root, at ``x = 0``, and ``a = -0.9999`` lies ``1e-4`` from -1: a shift along x by more than
    ``1e-4`` changes the sign of ``f(b)``, or evaluates the series outside ``(-1, 1)``.
    """

    number = (1, 1, 2, 4)
    name = "Problem 3"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            'Dowell, M., Jarratt, P. (1972). The "Pegasus" method for computing the root of an '
            "equation. BIT 12(4), 503–508. https://doi.org/10.1007/BF01932959."
        ),
        location="Problem 3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x`` and add ``c``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - 1.0 * c
            f_offset = 0.0
        else:
            f_offset = c
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
                    return total - 1.0 + f_offset
                total += term
                n += 1

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.9999, -0.0001)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=-0.69996, c=0.0, expected=-0.04892829857040081),
        FormulaTestCase.value(params={"modified": 0.0}, x=-0.69996, c=0.25, expected=-0.9973981399194692),
        FormulaTestCase.value(params={"modified": 0.0}, x=-0.9999, c=0.25, expected=math.nan),
        FormulaTestCase.value(params={"modified": 1.0}, x=-0.69996, c=0.25, expected=0.20107170142959918),
        FormulaTestCase.value(params={"modified": 1.0}, x=-0.0001, c=-0.25, expected=-0.24990001),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(-0.9999, -0.0001)),
    )
