"""This module holds a formula of Galdino (2011).

The formula comes from the row with the key ``f7`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Galdino2011F7(Formula):
    """This formula comes from Galdino (2011).

    The survey writes the source's function as ``exp((x - 3)^5) - exp(x - 1)``; the formula's interval is ``[4, 5]``.
    """

    number = (1, 2, 9, 7)
    name = "f7"
    params = ()
    source = FormulaSource(
        reference=(
            "Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011"
            " World Congress on Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN "
            "978-1-61284-365-0. No DOI; the author's copy: "
            "http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543."
        ),
        location="Table IV, f7",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1 \c"),),
        expression=r"e^{\left(\tmp{u} - 3\right)^{5}} - e^{\tmp{u} - 1}",
        interval="[4, 5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp((x - 3) ** 5) - math.exp(x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.3, c=0.0, expected=13.86104479377484),
        FormulaTestCase.value(params={}, x=4.3, c=0.25, expected=-17.532053742823347),
        FormulaTestCase.interval_bounds(params={}, expected=(4.0, 5.0)),
    )
