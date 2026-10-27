"""This module holds formula f1.99.3.5.13, the modified version of the published formula f1.3.5.13.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.5.13 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBorchers2026522(Formula):
    """This formula is the modified version of formula f1.3.5.13, from Borchers (2026).

    The survey writes the source's function as ``x*sin(pi*x)``; the published interval is ``[-2, 2]``.

    `findzeros` returns every root in the interval: -2, -1, 0, 1, 2

    The formula changes the interval ``[-2, 2]`` to ``[-2.04, 1.96]``: the interval moves left by 1% of the published
    interval's width, rounded half up to 1 significant digit, so that neither bound is a root. ``c`` shifts x by the
    rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval's bounds are the roots -2 and 2, where float64 ``pi`` makes ``f`` slightly negative at both, so that
    ``f(a)`` and ``f(b)`` have the same sign.

    The modification changes what the test problem tests: the source gives ``[-2, 2]`` to ``findzeros``, which returns
    every root in an interval, and a solver on ``[-2.04, 1.96]`` finds 1 of the 4 roots in that interval.
    """

    number = (1, 99, 3, 5, 13)
    name = "5.2.2"
    param_names = ()
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="5.2.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 4.0 * c
        return x * math.sin(math.pi * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.04, 1.96)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.84, c=0.25, expected=-0.8864267603471567),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.04, 1.96)),
    )
