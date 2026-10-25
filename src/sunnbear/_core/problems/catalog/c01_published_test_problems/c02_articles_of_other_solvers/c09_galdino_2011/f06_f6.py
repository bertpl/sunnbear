"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f6`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Galdino2011F6(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``exp((x - 3)^5) - 1``; the formula's interval is ``[2.5, 3.5]``.

    The appendix states a zero of multiplicity 5 at `x = 3`, under the label `f7`.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``expm1((x - 3)**5)``, on
    the published interval, and ``c`` shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``exp((x - 3)**5)`` rounds to 1, and the subtraction of 1 cancels, so that f is exactly 0 at many
    x-values within about 7e-4 of the root; ``expm1`` computes ``exp(u) - 1`` without the subtraction.
    """

    number = (1, 2, 9, 6)
    name = "f6"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011"
            " World Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN "
            "978-1-61284-365-0. No DOI; the author's copy: "
            "http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        location="f6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``expm1((y - 3)**5)``, with ``y = x - c_scale*c``. Category 1 states the
        rule for ``c_scale``.
        """
        x = x - 1.0 * c
        if modified == 1:
            return math.expm1((x - 3) ** 5)
        else:
            return math.exp((x - 3) ** 5) - 1

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.5, 3.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=2.8, c=0.0, expected=-0.00031994880546089787),
        FormulaTestCase.value(params={"modified": 0.0}, x=2.8, c=0.25, expected=-0.018283601758623744),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(2.5, 3.5)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(2.5, 3.5)),
        FormulaTestCase.value(params={"modified": 1.0}, x=2.8, c=0.25, expected=-0.018283601758623744),
    )
