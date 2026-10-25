"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.4`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.math_functions import sign


class OliveiraTakahashi202124(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``sign(3*x + 1)*(1 - sqrt(1 - (3*x + 1)^2/9^2))``; the formula's interval
    is ``[-1, 1]``.

    With ``modified = 1``, the formula computes the published function in the equivalent form
    ``sign(3*x + 1) * ((3*x + 1)**2/9**2) / (1 + sqrt(1 - (3*x + 1)**2/9**2))``, on the published interval, and ``c``
    shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``sqrt(1 - (3*x + 1)**2/9**2)`` rounds to 1, and its subtraction from 1 cancels, so that f is exactly
    0 at many x-values within about 2e-8 of the root; the equivalent form has no subtraction that cancels.
    """

    number = (1, 1, 9, 15)
    name = "2.4"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Oliveira, I. F. D., Takahashi, R. H. C. (2021). An enhancement of the bisection method "
            "average performance preserving minmax optimality. ACM Transactions on Mathematical "
            "Software 47(1), Article 5. https://doi.org/10.1145/3423597. The article itself is dated "
            "December 2020."
        ),
        location="2.4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as
        ``sign(3*y + 1) * ((3*y + 1)**2/9**2) / (1 + sqrt(1 - (3*y + 1)**2/9**2))``, with ``y = x - c_scale*c``.
        Category 1 states the rule for ``c_scale``.
        """
        x = x - 2.0 * c
        if modified == 1:
            return sign(3 * x + 1) * ((3 * x + 1) ** 2 / 9**2) / (1 + math.sqrt(1 - (3 * x + 1) ** 2 / 9**2))
        else:
            return sign(3 * x + 1) * (1 - math.sqrt(1 - (3 * x + 1) ** 2 / 9**2))

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=-0.4, c=0.0, expected=-0.00024694407093399845),
        FormulaTestCase.value(params={"modified": 0.0}, x=-0.4, c=0.25, expected=-0.018001533782093432),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=-0.4, c=0.25, expected=-0.018001533782093432),
    )
