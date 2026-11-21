"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f1`` in the survey of published test problems.
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


class Borchers2026F1(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``x^2*(x^2/3 + sqrt(2)*sin(x)) - sqrt(3)/18``; the formula's interval is
    ``[0, 1.2]``.

    Printed root: `0.3994222917`
    """

    number = (1, 3, 5, 1)
    name = "f1"
    params = ()
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="§5.6, f1",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.2 \c"),),
        expression=(
            r"\tmp{u}^{2} \left(\frac{\tmp{u}^{2}}{3} + \sqrt{2} \sin{\left(\tmp{u} \right)}\right) - "
            r"\frac{\sqrt{3}}{18}"
        ),
        interval="[0, 1.2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return x**2 * (x**2 / 3 + math.sqrt(2) * math.sin(x)) - math.sqrt(3) / 18

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.2)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.36, c=0.0, expected=-0.02606077147589848),
        FormulaTestCase.value(params={}, x=0.36, c=0.25, expected=-0.09591543798455478),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.2)),
    )
