"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.16`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Problem516(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``1 - Q^2/(g*Ac^3)*B``, with the parameters `Q = 20` m^3/s, `g = 9.81`
    m/s^2, `B = 3 + y`, `Ac = 3*y + y^2/2`; the formula's interval is ``[0.5, 2.5]``.

    Unknown ``y``, the critical depth (m); ``B`` is the width at the surface and ``Ac`` the cross-sectional area.
    Graphically, and by bisection and false position to ``es = 1%`` or at most 10 iterations.

    The formula's ``x`` is the source's depth ``y``.
    """

    number = (1, 4, 6, 21)
    name = "Problem 5.16"
    params = ()
    location_in_publication = "Prob. 5.16"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{y}", r"\x - 2 \c"),
            (r"\tmp{B}", r"3 + \tmp{y}"),
            (r"\tmp{A_c}", r"3 \tmp{y} + \frac{\tmp{y}^2}{2}"),
        ),
        expression=r"1 - \frac{20^2}{9.81 \tmp{A_c}^3} \tmp{B}",
        interval="[0.5, 2.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        surface_width = 3.0 + x
        area = 3.0 * x + x**2 / 2.0
        return 1.0 - 20.0**2 / (9.81 * area**3) * surface_width

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 2.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.1, c=0.0, expected=-1.8074480329135572),
        FormulaTestCase.value(params={}, x=1.1, c=0.25, expected=-17.910278020703927),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 2.5)),
    )
