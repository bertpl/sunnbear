"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``2.1-11; 2.2-6; 2.4-5; 2.5-7`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Bradie20062111(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``x^3 - 13``; the formula's interval is `(2, 3)` (2.2-6, 2.4-5, 2.5-7).

    Root `13^(1/3)`. 2.1-11 asks for 3 decimal places by bisection, with no interval.
    """

    number = (1, 4, 4, 16)
    name = "2.1-11"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="2.1-11; 2.2-6; 2.4-5; 2.5-7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - 13

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=-0.8330000000000028),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=-4.384875000000002),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
