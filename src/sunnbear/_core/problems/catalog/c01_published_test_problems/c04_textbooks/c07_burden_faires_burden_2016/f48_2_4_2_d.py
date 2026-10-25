"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-2(d)`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BurdenFairesBurden2016242D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(3*x) - 27*x^6 + 27*x^4*exp(x) - 9*x^2*exp(2*x)``; the formula's
    interval is ``[3, 5]``.

    As 2.4-2(a). It equals `(exp(x) - 3*x^2)^3`, the cube of 2.3-6(e)'s function.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``(exp(x) - 3*x**2)**3``,
    on the published interval, and ``c`` shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the 4 terms of the published form cancel, so that f is exactly 0 at many x-values within about 4e-5
    of the root; in ``(exp(x) - 3*x**2)**3``, only the rounding of ``exp(x) - 3*x**2`` can change the sign of f, and
    ``exp(x) - 3*x**2`` has a simple root, so that the sign of f can be wrong only at x-values at most about 1 float64
    value away from the root.
    """

    number = (1, 4, 7, 48)
    name = "2.4-2(d)"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-2(d)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``(exp(y) - 3*y**2)**3``, with ``y = x - c_scale*c``. Category 1 states
        the rule for ``c_scale``.
        """
        x = x - 2.0 * c
        if modified == 1:
            return (math.exp(x) - 3 * x**2) ** 3
        else:
            return math.exp(3 * x) - 27 * x**6 + 27 * x**4 * math.exp(x) - 9 * x**2 * math.exp(2 * x)

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=4.4, c=0.0, expected=12765.110088002586),
        FormulaTestCase.value(params={"modified": 0.0}, x=3.6, c=0.25, expected=-291.7044964422511),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(3.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(3.0, 5.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=3.6, c=0.25, expected=-291.7044964422511),
    )
