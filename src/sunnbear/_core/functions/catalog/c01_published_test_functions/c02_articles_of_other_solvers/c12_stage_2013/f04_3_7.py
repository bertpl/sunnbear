"""This module holds a formula of Stage (2013).

The formula comes from the row with the key ``3.7`` in the survey of published test problems. The survey describes this
function in words, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Stage201337(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``abs(x - 2/3)^0.5 - 0.1`` if ``x <= 2/3``; ``-abs(x - 2/3)^0.5 - 0.1``
    otherwise; the formula's interval is ``[-10, 10]``.
    """

    number = (1, 2, 12, 4)
    name = "3.7"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Stage, S. A. (2013). Comments on An Improvement to the Brent's Method. International "
            "Journal of Experimental Algorithms 4(1), 1–16. No DOI; the publisher's PDF: "
            "https://www.cscjournals.org/manuscript/Journals/IJEA/Volume4/Issue1/IJEA-33.pdf."
        ),
        location="3.7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 20.0 * c
        if x <= 2 / 3:
            return abs(x - 2 / 3) ** 0.5 - 0.1
        else:
            return -(abs(x - 2 / 3) ** 0.5) - 0.1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=2.060246899469287),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=3.009126351029605),
        FormulaTestCase.value(params={}, x=5.0, c=0.0, expected=-2.1816659994661327),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
