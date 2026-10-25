"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``§2.8 case (3); P34(iii)`` in the survey of published test problems. The
module generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Atkinson198928Case3(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``-1 + x*(3 + x*(-3 + x))``; the formula's interval is ``[0, 3]``.

    Triple root 1: Brent's algorithm takes 50 iterations to reach 1.000001, where bisection would take 19.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``(x - 1)**3``, on the
    published interval, and ``c`` shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 7e-6 of
    the root; ``(x - 1)**3`` has no terms that cancel.
    """

    number = (1, 4, 1, 6)
    name = "§2.8 case (3)"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="§2.8 case (3); P34(iii)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, as ``(x - c_scale*c - 1)**3`` with ``modified = 1``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 3.0 * c
        if modified == 1:
            return (x - 1) ** 3
        else:
            return -1 + x * (3 + x * (-3 + x))

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=0.9, c=0.0, expected=-0.0009999999999999994),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.9, c=0.25, expected=-0.6141249999999999),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(0.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(0.0, 3.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.9, c=0.25, expected=-0.6141249999999999),
    )
