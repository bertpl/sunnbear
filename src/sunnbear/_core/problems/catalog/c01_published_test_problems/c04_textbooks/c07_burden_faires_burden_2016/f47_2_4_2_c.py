"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-2(c)`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BurdenFairesBurden2016242C(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``sin(x)^3 + 3*exp(-2*x)*sin(x) - 3*exp(-x)*sin(x)^2 - exp(-3*x)``; the
    formula's interval is ``[3, 4]``.

    As 2.4-2(a). The book prints `sin 3x` and `sin 2x`, misprints for `sin(x)^3` and `sin(x)^2`: with them the 4 terms
    are the expansion of `(sin(x) - exp(-x))^3`, the cube of 2.3-6(f)'s function on the same `[3, 4]`, with a triple
    root at 3.096364. Every other part of 2.4-1 and 2.4-2 has a multiple root too (2.4-2(b) once its misprint is
    corrected). As printed, the function has a simple root at 3.141568.
    """

    number = (1, 4, 7, 47)
    name = "2.4-2(c)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.4-2(c)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (
            math.sin(x) ** 3
            + 3 * math.exp(-2 * x) * math.sin(x)
            - 3 * math.exp(-x) * math.sin(x) ** 2
            - math.exp(-3 * x)
        )

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=3.3, c=0.0, expected=-0.007372617909661088),
        FormulaTestCase.value(params={}, x=3.3, c=0.25, expected=8.579948567035882e-05),
        FormulaTestCase.interval_bounds(params={}, expected=(3.0, 4.0)),
    )
