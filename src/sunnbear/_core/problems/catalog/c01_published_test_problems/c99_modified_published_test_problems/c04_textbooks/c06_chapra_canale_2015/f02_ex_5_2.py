"""This module holds formula f1.99.4.6.2, the modified version of the published formula f1.4.6.2.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.6.2 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedChapraCanale2015Ex52(Formula):
    """This formula is the modified version of formula f1.4.6.2, from Chapra, Canale (2015).

    The survey writes the source's function as ``sin(10*x) + cos(3*x)``; the published intervals are `[0, 5]`; `[3, 5]`
    (Fig. 5.4(b)); `[4.2, 4.3]` (Fig. 5.4(c)).

    Several roots on the interval. Plots on narrower ranges (Fig. 5.4) show that the apparent double root near 4.2 is 2
    distinct roots, at about 4.23 and 4.26.

    The formula holds only the test problems on ``[3, 5]`` and ``[4.2, 4.3]``. It changes these intervals to
    ``[3.3, 5]`` and ``[4.2, 4.26]``, so that each holds an odd number of roots: ``[3.3, 5]`` leaves out the root near
    3.26, and ``[4.2, 4.26]`` leaves out the root near 4.264; ``c`` shifts x by the rule of category 1, with ``c_scale``
    the rounded width of each new interval.

    The published test problems on ``[3, 5]`` and ``[4.2, 4.3]`` do not satisfy the benchmark suite inclusion
    conditions, because the 2 published intervals hold 6 and 2 roots, even numbers, so that ``f(a)`` and ``f(b)`` have
    the same sign.

    On ``[4.2, 4.26]``, the modification changes what the test problem tests: the source plots f on ``[4.2, 4.3]``
    (Fig. 5.4(c)) to show that the apparent double root near 4.2 is 2 distinct roots, and ``[4.2, 4.26]`` holds only
    the first of them, so the modified test problem does not test telling the 2 roots apart.
    """

    number = (1, 99, 4, 6, 2)
    name = "Ex. 5.2"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Ex. 5.2; Fig. 5.4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        return math.sin(10 * x) + math.cos(3 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (3.3, 5.0, 1.7),
                    (4.2, 4.26, 0.06),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 3.3, "b": 5.0, "c_scale": 1.7}, x=3.81, c=0.25, expected=-0.09507589774771713
        ),
        FormulaTestCase.value(
            params={"a": 4.2, "b": 4.26, "c_scale": 0.06}, x=4.218, c=0.25, expected=0.07098460158622959
        ),
        FormulaTestCase.interval_bounds(params={"a": 3.3, "b": 5.0, "c_scale": 1.7}, expected=(3.3, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": 4.2, "b": 4.26, "c_scale": 0.06}, expected=(4.2, 4.26)),
    )
