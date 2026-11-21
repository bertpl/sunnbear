"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``5.2.2`` in the survey of published test problems.
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


class Borchers2026522(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``x*sin(pi*x)``; the formula's interval is ``[-2, 2]``.

    `findzeros` returns every root in the interval: -2, -1, 0, 1, 2
    """

    number = (1, 3, 5, 13)
    name = "5.2.2"
    params = ()
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="§5.2.2",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 4 \c"),),
        expression=r"\tmp{u} \sin{\left(\pi \tmp{u} \right)}",
        interval="[-2, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return x * math.sin(math.pi * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.8, c=0.0, expected=0.47022820183397845),
        FormulaTestCase.value(params={}, x=-0.8, c=0.25, expected=-1.0580134541264514),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 2.0)),
    )
