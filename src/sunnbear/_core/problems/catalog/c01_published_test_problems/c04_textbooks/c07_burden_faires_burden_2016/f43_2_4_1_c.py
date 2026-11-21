"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-1(c)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden2016241C(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - 3*x^2*(2^-x) + 3*x*(4^-x) - 8^-x``; the formula's interval is
    ``[0, 1]``.

    As 2.4-1(a). It equals `(x - 2^-x)^3`, the cube of 2.1-5(a)'s function.
    """

    number = (1, 4, 7, 43)
    name = "2.4-1(c)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-1(c)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 - 3 * x**2 * (2**-x) + 3 * x * (4**-x) - 8**-x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.13441631843652777),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.7684150363472455),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
