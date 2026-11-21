"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``§2.8 case (2); P34(ii); P14`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Atkinson198928Case2(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``x^2 - 1``; the formula's interval is ``[0, 3]``.

    Root 1 (Table 2.14). P14 runs Newton from `x0 = 100,000`.
    """

    number = (1, 4, 1, 5)
    name = "§2.8 case (2)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="§2.8 case (2); P34(ii); P14",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x**2 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.0, expected=-0.18999999999999995),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-0.9775),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
