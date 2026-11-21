"""This module holds a formula of Stage (2013).

The formula comes from the row with the key ``3.5`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Stage201335(Formula):
    """This formula comes from Stage (2013).

    The survey writes the source's function as ``cos(x) - x``; the formula's interval is ``[-10, 10]``.
    """

    number = (1, 2, 12, 2)
    name = "3.5"
    params = ()
    source = FormulaSource(
        reference=(
            "Stage, S. A. (2013). Comments on An Improvement to the Brent's Method. International "
            "Journal of Experimental Algorithms 4(1), 1–16. No DOI; the publisher's PDF: "
            "https://www.cscjournals.org/manuscript/Journals/IJEA/Volume4/Issue1/IJEA-33.pdf."
        ),
        location="3.5",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return math.cos(x) - x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=3.346356379136388),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=8.088869738115323),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
