"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.4-1(d); 2.5-2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016Exercise241D(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``exp(6*x) + 3*(log(2))^2*exp(2*x) - log(8)*exp(4*x) - (log(2))^3``; the
    formula's interval is ``[-1, 0]``.

    As 2.4-1(a). It equals `(exp(2*x) - log(2))^3`. 2.5-2 runs Newton from `p0 = 0` until `abs(p_{n+1} - p_n) < 0.0002`,
    then Aitken's method.
    """

    number = (1, 4, 7, 44)
    name = "Exercise 2.4-1(d)"
    params = ()
    location_in_publication = "Exercises 2.4-1(d), 2.5-2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"e^{6 \tmp{u}} + 3 \ln{\left(2 \right)}^{2} e^{2 \tmp{u}} - \ln{\left(8 \right)} e^{4 "
            r"\tmp{u}} - \ln{\left(2 \right)}^{3}"
        ),
        interval="[-1, 0]",
        summary=(
            r"The cube $(e^{2\tmp{u}} - \ln(2))^3$ written out, below $10^{-3}$ in magnitude on a band 0.145 wide "
            r"around the triple root."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

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
