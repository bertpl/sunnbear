"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-1(d); 2.5-2`` in the survey of published test problems. A change of
the formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden2016241D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(6*x) + 3*(log(2))^2*exp(2*x) - log(8)*exp(4*x) - (log(2))^3``; the
    formula's interval is ``[-1, 0]``.

    As 2.4-1(a). It equals `(exp(2*x) - log(2))^3`. 2.5-2 runs Newton from `p0 = 0` until `abs(p_{n+1} - p_n) < 0.0002`,
    then Aitken's method.
    """

    number = (1, 4, 7, 44)
    name = "2.4-1(d)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-1(d); 2.5-2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (
            math.exp(6 * x)
            + 3 * (math.log(2)) ** 2 * math.exp(2 * x)
            - math.log(8) * math.exp(4 * x)
            - (math.log(2)) ** 3
        )

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 0.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.7, c=0.0, expected=-0.08904528189701376),
        FormulaTestCase.value(params={}, x=-0.7, c=0.25, expected=-0.16061531716931451),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 0.0)),
    )
