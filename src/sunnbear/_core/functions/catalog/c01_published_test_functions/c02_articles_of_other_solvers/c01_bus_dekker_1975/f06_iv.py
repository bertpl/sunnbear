"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``IV`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BusDekker1975Iv(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``0`` if ``x = 0``; ``x*exp(-x^-2)`` otherwise; the formula's interval is
    ``[-1, 4]``.

    Group IV: all derivatives vanish at the zero, which the article calls a multiplicity of infinity.
    """

    number = (1, 2, 1, 6)
    name = "IV"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Bus, J. C. P., Dekker, T. J. (1975). Two efficient algorithms with guaranteed convergence "
            "for finding a zero of a function. ACM Transactions on Mathematical Software 1(4), 330–345."
            " https://doi.org/10.1145/355656.355659."
        ),
        location="IV",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        # below 1e-100, float64 rounds x*exp(-x^-2) to 0, and x**-2 overflows
        if abs(x) < 1e-100:
            return 0.0
        else:
            return x * math.exp(-(x**-2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(params={}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={}, x=1e-200, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 4.0)),
    )
