"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``§8.4, (8.23), Fig. 8.6`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ChapraCanale2015Figure86(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``f = 0.25/(log10(eps/(3.7*D) + 2.51/(Re*sqrt(f))))^2``, with the
    parameters `Re = rho*V*D/mu`; `rho = 1.23` kg/m^3, `mu = 1.79E-5` N s/m^2, `D = 0.005` m, `V = 40` m/s, `eps =
    1.5E-6` m (the book's 0.0015 mm), so `Re = 13743` (§8.4); the formula's interval is ``[0.008, 0.08]``.

    (8.21) solved for its first ``f``; the book prints ``log``, base 10. Fixed-point iteration from any guess in the
    interval reaches an error below 0.008% in 6 or fewer iterations.

    The formula's ``x`` is the source's friction factor ``f``, and the formula is the difference form ``f -
    0.25/(...)^2`` of the fixed-point equation, with the values of Section 8.4's example: ``eps = 1.5E-6``, and ``Re =
    rho*V*D/mu`` computed as the book's MATLAB code computes it.
    """

    number = (1, 4, 6, 9)
    name = "Figure 8.6"
    params = ()
    location_in_publication = "§8.4, Eq. (8.23), Fig. 8.6"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - 0.072 \c"),
            (r"\tmp{\mathrm{Re}}", r"\frac{1.23 \cdot 40 \cdot 0.005}{1.79 \cdot 10^{-5}}"),
        ),
        expression=(
            r"\tmp{u} - \frac{0.25}{\left(\log_{10}\left(\frac{1.5 \cdot 10^{-6}}{3.7 \cdot 0.005} "
            r"+ \frac{2.51}{\tmp{\mathrm{Re}} \sqrt{\tmp{u}}}\right)\right)^2}"
        ),
        interval="[0.008, 0.08]",
        summary=(
            "The fixed-point form of the Colebrook equation for the friction factor, increasing and concave above a "
            "double pole, with 1 simple root above that pole."
        ),
        notes=(r"$\tmp{u}$ is the source's variable $f$, the friction factor.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.072 * c
        # the formula is the difference form x - 0.25/(...)^2 of the fixed-point equation (8.23), with the values
        # of Section 8.4's example
        diameter, eps = 0.005, 1.5e-6
        reynolds = 1.23 * 40.0 * diameter / 1.79e-5
        return x - 0.25 / math.log10(eps / (3.7 * diameter) + 2.51 / (reynolds * math.sqrt(x))) ** 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.008, 0.08)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.0296, c=0.0, expected=0.0007179248847414975),
        FormulaTestCase.value(params={}, x=0.0296, c=0.25, expected=-0.021449364335113793),
        FormulaTestCase.interval_bounds(params={}, expected=(0.008, 0.08)),
    )
