"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-2(d)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden2016242D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(3*x) - 27*x^6 + 27*x^4*exp(x) - 9*x^2*exp(2*x)``; the formula's
    interval is ``[3, 5]``.

    As 2.4-2(a). It equals `(exp(x) - 3*x^2)^3`, the cube of 2.3-6(e)'s function.
    """

    number = (1, 4, 7, 48)
    name = "2.4-2(d)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-2(d)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return math.exp(3 * x) - 27 * x**6 + 27 * x**4 * math.exp(x) - 9 * x**2 * math.exp(2 * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.4, c=0.0, expected=12765.110088002586),
        FormulaTestCase.value(params={}, x=3.6, c=0.25, expected=-291.7044964422511),
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 5.0)),
    )
