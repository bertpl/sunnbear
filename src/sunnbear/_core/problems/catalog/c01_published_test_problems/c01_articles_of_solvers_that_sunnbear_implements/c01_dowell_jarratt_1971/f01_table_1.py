"""This module holds a formula of Dowell, Jarratt (1971).

The formula comes from the row with the key ``Table 1`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class DowellJarratt1971Table1(Formula):
    """This formula comes from Dowell, Jarratt (1971).

    The survey writes the source's function as ``sin(x) - 0.5``; the formula's interval is ``[0, 1.5]``.

    Root `pi/6`. Starting values `x0 = 0.0`, `x1 = 1.5`.
    """

    number = (1, 1, 1, 1)
    name = "Table 1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return math.sin(x) - 0.5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=-0.06503446588876978),
        FormulaTestCase.value(params={}, x=0.45, c=0.25, expected=-0.42507029272725766),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
