"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-1`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BurdenFairesBurden2016211(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``sqrt(x) - cos(x)``; the formula's interval is ``[0, 1]``.

    Bisection to `p3`.

    With ``modified = 1``, the formula keeps the published interval, evaluates the published function at x without
    shifting x, and adds ``c`` to the function's value.

    The published test function does not satisfy the benchmark suite inclusion conditions, because a shift along x by
    any ``c > 0`` evaluates ``sqrt(x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 4, 7, 9)
    name = "2.1-1"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-1",
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
        return math.sqrt(x) - math.cos(x) + f_offset

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published test function, then its modified version."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=0.3, c=0.0, expected=-0.4076139316204399),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.3, c=0.25, expected=-0.7751434626449873),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.3, c=0.25, expected=-0.1576139316204399),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.0, c=0.25, expected=-0.75),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(0.0, 1.0)),
    )
