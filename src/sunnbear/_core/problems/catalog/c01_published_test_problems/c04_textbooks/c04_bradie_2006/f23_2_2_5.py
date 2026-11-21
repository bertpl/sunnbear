"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.2-5; 2.4-4; 2.5-6`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Bradie2006225(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^7 = 3``; the formula's interval is ``(1, 2)``.

    Root `3^(1/7)`. False position, Newton and secant.
    """

    number = (1, 4, 4, 23)
    name = "2.2-5"
    params = ()
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="2.2-5; 2.4-4; 2.5-6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x**7) - (3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.3, c=0.0, expected=3.2748517000000015),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-1.5928995773437495),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
    )
