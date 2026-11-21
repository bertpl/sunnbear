"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.6-7`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden2016267(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``600*x^4 - 550*x^3 + 200*x^2 - 20*x - 1``; the formula's interval is
    ``[0.1, 1]``.

    A solution in the interval to `1E-4` by bisection, Newton, secant, false position and Müller's method.
    """

    number = (1, 4, 7, 50)
    name = "2.6-7"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.6-7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.9 * c
        return 600 * x**4 - 550 * x**3 + 200 * x**2 - 20 * x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.37, c=0.0, expected=2.3658159999999997),
        FormulaTestCase.value(params={}, x=0.37, c=0.25, expected=-1.106513375),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 1.0)),
    )
