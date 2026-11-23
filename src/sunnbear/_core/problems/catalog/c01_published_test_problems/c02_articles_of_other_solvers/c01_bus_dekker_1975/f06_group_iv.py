"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``IV`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BusDekker1975GroupIv(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``0`` if ``x = 0``; ``x*exp(-x^-2)`` otherwise; the formula's interval is
    ``[-1, 4]``.

    Group IV: all derivatives vanish at the zero, which the article calls a multiplicity of infinity.
    """

    number = (1, 2, 1, 6)
    name = "Group IV"
    params = ()
    location_in_publication = "Group IV"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } |\tmp{u}| < 10^{-100} \\ "
            r"\tmp{u} e^{-\tmp{u}^{-2}} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[-1, 4]",
        summary=(
            r"An odd function with all derivatives 0 at its root, so flat there that it is exactly 0 in floating point "
            r"on a band 0.073 wide."
        ),
        notes=(
            r"The expression is 0 for $|\tmp{u}| < 10^{-100}$, where float64 rounds $\tmp{u} e^{-\tmp{u}^{-2}}$ to 0 "
            r"anyway; the published function is 0 only at $\tmp{u} = 0$.",
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

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
