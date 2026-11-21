"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-6(b)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden2016236B(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``log(x - 1) + cos(x - 1)``; the formula's interval is ``[1.3, 2]``.

    As 2.3-6(a).
    """

    number = (1, 4, 7, 35)
    name = "2.3-6(b)"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.3-6(b)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.7 * c
        return math.log(x - 1) + math.cos(x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.3, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.51, c=0.0, expected=0.19939995438198568),
        FormulaTestCase.value(params={}, x=1.51, c=0.25, expected=-0.1492144375244277),
        FormulaTestCase.interval_bounds(params={}, expected=(1.3, 2.0)),
    )
