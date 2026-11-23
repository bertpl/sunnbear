"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``§2 (p. 55); §2.2 (p. 78); 2.2-15`` in the survey of published test
problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Bradie2006Section2Page55(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``(rho_f/3)*h^3 - R*rho_f*h^2 + (4/3)*R^3*rho_o``, with the parameters `R
    = 5` cm, `rho_o = 0.120`, `rho_f = 0.890` g/cm^3 (§2.2); the formula's interval is `(0, 10)` (§2.2).

    Unknown `h`, the depth to which a sphere of radius `R` and density `rho_o` sinks in a fluid of density `rho_f`; the
    derivation assumes the sphere is not fully submerged. False position on `(0, 10)` with tolerance `5E-5` gives `p5 =
    2.3043353119`. 2.2-15 reworks the problem for a glass marble, `R = 2`, `rho_o = 0.040`, `rho_f = 0.998`, and gives
    no interval. The marble's cubic has its physical root at about 0.48212, but no sign change on `(0, 10)`: the cubic
    also has the root 5.96394 there, beyond the marble's diameter `2*R = 4`, where the derivation no longer holds.
    """

    number = (1, 4, 4, 1)
    name = "Section 2 (page 55)"
    params = (
        FormulaParam("R", latex_symbol="R", meaning="The sphere's radius."),
        FormulaParam("rho_o", latex_symbol=r"\rho_{o}", meaning="The sphere's density."),
        FormulaParam("rho_f", latex_symbol=r"\rho_{f}", meaning="The fluid's density."),
    )
    location_in_publication = "§2 (p. 55); §2.2 (p. 78); Exercise 2.2-15"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{h}", r"\x - 10 \c"),),
        expression=(
            r"\frac{\param{rho_f}}{3} \tmp{h}^{3} - \param{R} \param{rho_f} \tmp{h}^{2} + \frac{4 "
            r"\param{R}^{3} \param{rho_o}}{3}"
        ),
        interval="[0, 10]",
        summary=(
            "A decreasing cubic for the depth to which a floating sphere sinks, with 1 simple root and a slope of 0 at "
            "both bounds."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, R: float, rho_o: float, rho_f: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        return (rho_f / 3) * x**3 - R * rho_f * x**2 + (4 / 3) * R**3 * rho_o

    def interval_bounds(self, R: float, rho_o: float, rho_f: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("R", "rho_o", "rho_f"), rows=((5.0, 0.12, 0.89),), summary="The published parameter values."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"R": 5.0, "rho_o": 0.12, "rho_f": 0.89}, x=3.0, c=0.0, expected=-12.04),
        FormulaTestCase.value(
            params={"R": 5.0, "rho_o": 0.12, "rho_f": 0.89}, x=3.0, c=0.25, expected=18.924583333333334
        ),
        FormulaTestCase.interval_bounds(params={"R": 5.0, "rho_o": 0.12, "rho_f": 0.89}, expected=(0.0, 10.0)),
    )
