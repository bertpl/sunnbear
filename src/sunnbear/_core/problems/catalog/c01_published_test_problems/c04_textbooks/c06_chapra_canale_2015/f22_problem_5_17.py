"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.17, 5.19, 6.19, 8.9`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class ChapraCanale2015Problem517(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``V = pi*h^2*(3*R - h)/3``, with the parameters `R = 3` m, `V = 30` m^3
    (5.17, 6.19); the formula's interval is `[0, 3]` (5.17).

    Unknown `h`, the depth of water in a spherical tank of radius `R`: 3 false-position iterations on `[0, R]` (5.17); 3
    Newton iterations from `h0 = R`, which the book says always converges (6.19). Prob. 8.9 asks for `h` at `R = 1` m
    (written `r`) and `V = 0.5` m^3, and gives no interval or starting point. In Prob. 5.19, `h` is the height above
    water of a floating sphere, which the problem asks for by bisection, with no interval. The problem gives `r = 1` m,
    the densities `rho_s = 200` and `rho_w = 1000` kg/m^3 of the sphere and the water, the volume of the cap above
    water, and Archimedes' principle, so that `R = 1` m and `V = (4/3)*pi*r^3*(1 - rho_s/rho_w) = 3.35103216383` m^3;
    the book does not print that value of `V`. Prob. 8.10 gives 2 fixed-point forms.
    """

    number = (1, 4, 6, 22)
    name = "Problem 5.17"
    params = (
        FormulaParam("R", latex_symbol="R", meaning="The tank's radius, in m."),
        FormulaParam("V", latex_symbol="V", meaning=r"The volume of water in the tank, in $\mathrm{m^3}$."),
    )
    location_in_publication = "Prob. 5.17, 5.19, 6.19, 8.9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"\param{V} - \frac{\pi \tmp{u}^{2} \left(3 \param{R} - \tmp{u}\right)}{3}",
        interval="[0, 3]",
        summary=(
            "A cubic with 1 simple root, the depth at which a spherical tank holds a given volume of water, and a local"
            " maximum 2.03 below that root."
        ),
        notes=(r"$\tmp{u}$ is the source's variable $h$, the depth of the water in the tank, in m.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, R: float, V: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return (V) - (math.pi * x**2 * (3 * R - x) / 3)

    def interval_bounds(self, R: float, V: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("R", "V"), rows=((3.0, 30.0),), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"R": 3.0, "V": 30.0}, x=0.9, c=0.0, expected=23.12933686659912),
        FormulaTestCase.value(params={"R": 3.0, "V": 30.0}, x=0.9, c=0.25, expected=29.791476787617977),
        FormulaTestCase.interval_bounds(params={"R": 3.0, "V": 30.0}, expected=(0.0, 3.0)),
    )
