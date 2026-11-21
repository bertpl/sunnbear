"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``T2.6`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Sabharwal2019T26(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x^2 + 5*x + 2``; the formula's interval is ``[-6, 0]``.

    No sign change on `[-6, 0]`, which holds both roots, `(-5 - sqrt(17))/2` and `(-5 + sqrt(17))/2`.
    """

    number = (1, 2, 13, 8)
    name = "T2.6"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula "
            "Falsi Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        location="T2.6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 6.0 * c
        return x**2 + 5 * x + 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-6.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.2, c=0.0, expected=-1.3599999999999994),
        FormulaTestCase.value(params={}, x=-4.2, c=0.25, expected=5.990000000000001),
        FormulaTestCase.interval_bounds(params={}, expected=(-6.0, 0.0)),
    )
