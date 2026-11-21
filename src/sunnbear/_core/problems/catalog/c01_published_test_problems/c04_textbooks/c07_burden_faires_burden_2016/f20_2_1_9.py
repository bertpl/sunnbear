"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-9`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden2016219(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(x) - 2 = cos(exp(x) - 2)``; the formula's interval is ``[0.5,
    1.5]``.

    Bisection to `1E-5`, after a sketch of both sides.
    """

    number = (1, 4, 7, 20)
    name = "2.1-9"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-9",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (math.exp(x) - 2) - (math.cos(math.exp(x) - 2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.8, c=0.0, expected=-0.7491323513800876),
        FormulaTestCase.value(params={}, x=0.8, c=0.25, expected=-1.2313804597298508),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.5)),
    )
