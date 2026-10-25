"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``Ex. 2.10; 2.5-11(a); 2.6-4, 2.6-12, 2.6-13`` in the survey of published
test problems. The module generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula
with the parameter ``modified``, which selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Bradie2006Ex210(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x*(1 - cos(x))``; the formula's interval is `[-2, 1]` (Ex. 2.10).

    Root 0 of multiplicity 3. Newton from `p0 = 1` converges linearly, at rate 2/3, and bisection on `[-2, 1]` beats it
    (Ex. 2.10); secant from `p0 = -1, p1 = 2` (2.5-11); Aitken on the Newton sequence (2.6-4); both techniques for
    restoring quadratic convergence, from `p0 = 1` (2.6-12). 2.6-13 estimates the multiplicity 3 from the 2.6-4
    sequence.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``2*x*sin(x/2)**2``, on
    the published interval, and ``c`` shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``cos(x)`` rounds to 1, and ``1 - cos(x)`` cancels, so that f is exactly 0 at many x-values within
    about 1e-8 of the root; ``2*x*sin(x/2)**2`` has no subtraction.
    """

    number = (1, 4, 4, 28)
    name = "Ex. 2.10"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="Ex. 2.10; 2.5-11(a); 2.6-4, 2.6-12, 2.6-13",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``2*y*sin(y/2)**2``, with ``y = x - c_scale*c``. Category 1 states the
        rule for ``c_scale``.
        """
        x = x - 3.0 * c
        if modified == 1:
            return 2 * x * math.sin(x / 2) ** 2
        else:
            return x * (1 - math.cos(x))

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=-1.1, c=0.0, expected=-0.601044266431865),
        FormulaTestCase.value(params={"modified": 0.0}, x=-1.1, c=0.25, expected=-2.359841956625349),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(-2.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(-2.0, 1.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=-1.1, c=0.25, expected=-2.359841956625349),
    )
