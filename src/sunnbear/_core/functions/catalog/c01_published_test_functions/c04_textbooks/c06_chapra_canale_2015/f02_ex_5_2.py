"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Ex. 5.2; Fig. 5.4`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ChapraCanale2015Ex52(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``sin(10*x) + cos(3*x)``; the formula's intervals are `[0, 5]`; `[3, 5]`
    (Fig. 5.4(b)); `[4.2, 4.3]` (Fig. 5.4(c)).

    Several roots on the interval. Plots on narrower ranges (Fig. 5.4) show that the apparent double root near 4.2 is 2
    distinct roots, at about 4.23 and 4.26.

    With ``modified = 1``, the intervals ``[3, 5]`` and ``[4.2, 4.3]`` become ``[3.3, 5]`` and ``[4.2, 4.26]``, so that
    each holds an odd number of roots: the first loses its first root, near 3.26, and the second its second root, near
    4.264.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test functions on ``[3, 5]`` and ``[4.2, 4.3]`` fail a benchmark suite's checks of its test functions,
    because they hold 6 and 2 roots, even numbers, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 6, 2)
    name = "Ex. 5.2"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Ex. 5.2; Fig. 5.4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(10 * x) + math.cos(3 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.0, 5.0, 5.0, 0.0),
                    (3.0, 5.0, 2.0, 0.0),
                    (4.2, 4.3, 0.1, 0.0),
                ),
            ),
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (3.3, 5.0, 1.7, 1.0),
                    (4.2, 4.26, 0.06, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 5.0, "c_scale": 5.0, "modified": 0.0}, x=1.5, c=0.0, expected=0.4394920407263372
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 5.0, "c_scale": 5.0, "modified": 0.0}, x=1.5, c=0.25, expected=1.3301610129777774
        ),
        FormulaTestCase.value(
            params={"a": 3.0, "b": 5.0, "c_scale": 2.0, "modified": 0.0}, x=3.6, c=0.0, expected=-1.186108759898451
        ),
        FormulaTestCase.value(
            params={"a": 4.2, "b": 4.3, "c_scale": 0.1, "modified": 0.0}, x=4.23, c=0.0, expected=-0.0014226045479633668
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 5.0, "c_scale": 5.0, "modified": 0.0}, expected=(0.0, 5.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 3.0, "b": 5.0, "c_scale": 2.0, "modified": 0.0}, expected=(3.0, 5.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.2, "b": 4.3, "c_scale": 0.1, "modified": 0.0}, expected=(4.2, 4.3)
        ),
        FormulaTestCase.value(
            params={"a": 3.3, "b": 5.0, "c_scale": 1.7, "modified": 1.0}, x=3.81, c=0.25, expected=-0.09507589774771713
        ),
        FormulaTestCase.value(
            params={"a": 4.2, "b": 4.26, "c_scale": 0.06, "modified": 1.0},
            x=4.218,
            c=0.25,
            expected=0.07098460158622959,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 3.3, "b": 5.0, "c_scale": 1.7, "modified": 1.0}, expected=(3.3, 5.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 4.2, "b": 4.26, "c_scale": 0.06, "modified": 1.0}, expected=(4.2, 4.26)
        ),
    )
