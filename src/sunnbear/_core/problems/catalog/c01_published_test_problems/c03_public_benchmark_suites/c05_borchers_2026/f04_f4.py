"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f4`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Borchers2026F4(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``2*(x*exp(-9) - exp(-9*x)) + 1``; the formula's interval is ``[-0.5,
    0.7]``.

    Printed root: `0.07701424135`
    """

    number = (1, 3, 5, 4)
    name = "f4"
    param_names = ()
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="f4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return 2 * (x * math.exp(-9) - math.exp(-9 * x)) + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.5, 0.7)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.14, c=0.0, expected=-6.050877529475909),
        FormulaTestCase.value(params={}, x=-0.14, c=0.25, expected=-103.9147604988257),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.5, 0.7)),
    )
