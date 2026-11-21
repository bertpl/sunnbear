"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``T2.5`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Sabharwal2019T25(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x^2 + 2*x - 7``; the formula's interval is ``[1, 3]``.
    """

    number = (1, 2, 13, 7)
    name = "T2.5"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula "
            "Falsi Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        location="T2.5",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x**2 + 2 * x - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.6, c=0.0, expected=-1.2399999999999995),
        FormulaTestCase.value(params={}, x=1.6, c=0.25, expected=-3.5899999999999994),
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 3.0)),
    )
