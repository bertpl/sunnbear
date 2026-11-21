"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f2`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Borchers2026F2(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``11*x^11 - 1``; the formula's interval is ``[0.4, 1.6]``.

    Printed root: `0.8041330975`
    """

    number = (1, 3, 5, 2)
    name = "f2"
    param_names = ()
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="f2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.2 * c
        return 11 * x**11 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.4, 1.6)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.76, c=0.0, expected=-0.4625448852563808),
        FormulaTestCase.value(params={}, x=0.76, c=0.25, expected=-0.9978535101773714),
        FormulaTestCase.interval_bounds(params={}, expected=(0.4, 1.6)),
    )
