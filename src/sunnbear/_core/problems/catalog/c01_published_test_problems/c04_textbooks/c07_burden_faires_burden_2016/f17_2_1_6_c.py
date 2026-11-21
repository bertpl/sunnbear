"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-6(c); 2.3-12(a)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaParam, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BurdenFairesBurden2016216C(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^2 - 4*x + 4 - log(x)``; the formula's intervals are `[1, 2]`; `[2,
    4]`.

    Bisection to `1E-5` (2.1-6); Newton, secant and false position to `1E-7` (2.3-12).
    """

    number = (1, 4, 7, 17)
    name = "2.1-6(c)"
    params = (
        FormulaParam("a"),
        FormulaParam("b"),
        FormulaParam("c_scale"),
    )
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-6(c); 2.3-12(a)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**2 - 4 * x + 4 - math.log(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((1.0, 2.0, 1.0), (2.0, 4.0, 2.0))),)

    test_cases = (
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.0, expected=0.22763573553250885),
        FormulaTestCase.value(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.25, expected=0.8537098358305679),
        FormulaTestCase.value(params={"a": 2.0, "b": 4.0, "c_scale": 2.0}, x=2.6, c=0.0, expected=-0.5955114450274362),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 2.0, "c_scale": 1.0}, expected=(1.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 4.0, "c_scale": 2.0}, expected=(2.0, 4.0)),
    )
