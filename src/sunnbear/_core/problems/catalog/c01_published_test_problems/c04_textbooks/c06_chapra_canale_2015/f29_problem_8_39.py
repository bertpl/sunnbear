"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 8.39`` in the survey of published test problems.
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


class ChapraCanale2015Problem839(Formula):
    r"""This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``v = u*log(m0/(m0 - q*t)) - g*t``, with the parameters `u = 2200` m/s,
    `m0 = 160000` kg, `q = 2680` kg/s, `g = 9.81` m/s^2, `v = 1000` m/s; the formula's interval is ``[10, 50]``.

    Unknown `t`, the time at which the velocity is 1000 m/s, to within 1%; the book's hint gives the interval. The book
    prints `ln`.
    """

    number = (1, 4, 6, 29)
    name = "Problem 8.39"
    params = (
        FormulaParam(
            "uex", latex_symbol=r"u_{\mathrm{ex}}", meaning="The exhaust velocity relative to the rocket, in m/s."
        ),
        FormulaParam("m0", latex_symbol="m_{0}", meaning="The rocket's initial mass, in kg."),
        FormulaParam("q", latex_symbol="q", meaning="The rate of fuel consumption, in kg/s."),
        FormulaParam("g", latex_symbol="g", meaning=r"The gravitational acceleration, in $\mathrm{m/s^2}$."),
        FormulaParam("v", latex_symbol="v", meaning="The target velocity, in m/s."),
    )
    location_in_publication = "Prob. 8.39"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 100 \c"),),
        expression=(
            r"\param{v} - \left(\param{uex} \ln{\left(\frac{\param{m0}}{\param{m0} - \param{q} \tmp{u}} "
            r"\right)} - \param{g} \tmp{u}\right)"
        ),
        interval="[10, 50]",
        summary=(
            r"The rocket equation with a gravity term, in terms of the time, decreasing through 1 simple root toward a "
            r"logarithmic singularity at $\x = \param{m0}/\param{q} + 100 \c$."
        ),
        notes=(
            r"$\tmp{u}$ is the source's variable $t$, the time, in s.",
            r"$\param{uex}$ is the source's parameter $u$.",
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, uex: float, m0: float, q: float, g: float, v: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 100.0 * c
        return (v) - (uex * math.log(m0 / (m0 - q * x)) - g * x)

    def interval_bounds(self, uex: float, m0: float, q: float, g: float, v: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (10.0, 50.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("uex", "m0", "q", "g", "v"),
                rows=((2200.0, 160000.0, 2680.0, 9.81, 1000.0),),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"uex": 2200.0, "m0": 160000.0, "q": 2680.0, "g": 9.81, "v": 1000.0},
            x=22.0,
            c=0.0,
            expected=204.57385817849925,
        ),
        FormulaTestCase.value(
            params={"uex": 2200.0, "m0": 160000.0, "q": 2680.0, "g": 9.81, "v": 1000.0},
            x=22.0,
            c=0.1,
            expected=624.0524669251027,
        ),
        FormulaTestCase.interval_bounds(
            params={"uex": 2200.0, "m0": 160000.0, "q": 2680.0, "g": 9.81, "v": 1000.0}, expected=(10.0, 50.0)
        ),
    )
