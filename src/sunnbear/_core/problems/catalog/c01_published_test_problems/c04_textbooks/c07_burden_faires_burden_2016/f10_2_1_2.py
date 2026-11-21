"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BurdenFairesBurden2016212(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``3*(x + 1)*(x - 1/2)*(x - 1)``; the formula's intervals are `[-2, 1.5]`;
    `[-1.25, 2.5]`.

    Roots -1, 1/2 and 1. Bisection to `p3` on each interval.
    """

    number = (1, 4, 7, 10)
    name = "2.1-2"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 3 * (x + 1) * (x - 1 / 2) * (x - 1)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((-2.0, 1.5, 3.5), (-1.25, 2.5, 3.75))),)

    test_cases = (
        FormulaTestCase.value(
            params={"a": -2.0, "b": 1.5, "c_scale": 3.5}, x=-0.95, c=0.0, expected=0.42412500000000036
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 1.5, "c_scale": 3.5}, x=-0.95, c=0.25, expected=-16.256109374999998
        ),
        FormulaTestCase.value(params={"a": -1.25, "b": 2.5, "c_scale": 3.75}, x=-0.125, c=0.0, expected=1.845703125),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 1.5, "c_scale": 3.5}, expected=(-2.0, 1.5)),
        FormulaTestCase.interval_bounds(params={"a": -1.25, "b": 2.5, "c_scale": 3.75}, expected=(-1.25, 2.5)),
    )
