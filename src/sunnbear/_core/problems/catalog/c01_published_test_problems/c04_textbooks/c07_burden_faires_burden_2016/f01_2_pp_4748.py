"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2 (pp. 47–48); 2.3-22`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden20162Pp4748(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``1564000 = 1000000*exp(lambda) + (435000/lambda)*(exp(lambda) - 1)``;
    the formula's interval is `(0, 1]` (figure, p. 47).

    Unknown ``lambda``, the birthrate of a population. From the model ``N(t) = N0*exp(lambda*t) +
    (v/lambda)*(exp(lambda*t) - 1)`` with ``N0 = 1000000``, immigration ``v = 435000`` per year and ``N(1) = 1564000``;
    the figure on p. 47 plots ``N(lambda)`` in thousands up to ``lambda = 1``. 2.3-22 asks for ``lambda`` to ``1E-4``,
    then predicts the population after 2 years.

    The formula's ``x`` is the source's ``lambda``, and the formula is the difference form ``1564000 - (...)`` of the
    printed equation. The formula's interval is ``[0, 1]``; at ``x = 0``, where the source's function divides 0 by 0,
    the formula takes its limit, 129000.
    """

    number = (1, 4, 7, 1)
    name = "§2 (pp. 47–48)"
    params = ()
    location_in_publication = "§2 (pp. 47–48); Exercise 2.3-22"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{\lambda}", r"\x - \c"),),
        expression=(
            r"\begin{cases} "
            r"1564000 - (1000000 + 435000) & \text{if } \tmp{\lambda} = 0 \\ "
            r"1564000 - \left(1000000 e^{\tmp{\lambda}} + \frac{435000}{\tmp{\lambda}} (e^{\tmp{\lambda}} - 1)\right) "
            r"& \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        if x == 0.0:
            # at x = 0, (435000/x)*(exp(x) - 1) takes its limit 435000
            return 1564000.0 - (1000000.0 + 435000.0)
        else:
            return 1564000.0 - (1000000.0 * math.exp(x) + (435000.0 / x) * (math.exp(x) - 1.0))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-293154.07856120757),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=66670.36515256682),
        FormulaTestCase.value(params={}, x=0.0, c=0.0, expected=129000.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
