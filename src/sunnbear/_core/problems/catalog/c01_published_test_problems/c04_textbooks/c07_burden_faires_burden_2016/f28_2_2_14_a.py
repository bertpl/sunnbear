"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.2-14(a); 2.5-12(a)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden20162214A(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``2 + sin(x) - x``; the formula's interval is ``[2, 3]``.

    Fixed-point iteration to `1E-5` with a function `g` of the reader's choice (2.2-14); Steffensen's method on that `g`
    (2.5-12).
    """

    number = (1, 4, 7, 28)
    name = "2.2-14(a)"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.2-14(a); 2.5-12(a)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 2 + math.sin(x) - x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=0.4457052121767205),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=0.8373623686333757),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
