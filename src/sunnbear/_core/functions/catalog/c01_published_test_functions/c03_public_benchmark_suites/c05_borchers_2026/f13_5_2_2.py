"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``5.2.2`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Borchers2026522(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``x*sin(pi*x)``; the formula's interval is ``[-2, 2]``.

    `findzeros` returns every root in the interval: -2, -1, 0, 1, 2

    With ``modified = 1``, the interval ``[-2, 2]`` becomes ``[-2.04, 1.96]``: it moves left by 1% of the published
    interval's width, rounded half up to 1 significant digit, so that neither bound is a root.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because the published interval's
    bounds are the roots -2 and 2, where float64 evaluates ``f`` to about ``-5e-16`` at both, since float64 ``pi`` makes
    ``sin(pi*x)`` slightly nonzero.
    """

    number = (1, 3, 5, 13)
    name = "5.2.2"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test functions."
        ),
        location="5.2.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x * math.sin(math.pi * x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-2.0, 2.0, 4.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-2.04, 1.96, 4.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, x=-0.8, c=0.0, expected=0.47022820183397845
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, x=-0.8, c=0.25, expected=-1.0580134541264514
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, expected=(-2.0, 2.0)
        ),
        FormulaTestCase.value(
            params={"a": -2.04, "b": 1.96, "c_scale": 4.0, "modified": 1.0},
            x=-0.84,
            c=0.25,
            expected=-0.8864267603471567,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.04, "b": 1.96, "c_scale": 4.0, "modified": 1.0}, expected=(-2.04, 1.96)
        ),
    )
