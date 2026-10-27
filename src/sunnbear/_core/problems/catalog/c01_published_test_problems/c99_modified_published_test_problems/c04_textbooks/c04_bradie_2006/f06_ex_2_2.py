"""This module holds formula f1.99.4.4.6, the modified version of the published formula f1.4.4.6.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.4.6 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBradie2006Ex22(Formula):
    """This formula is the modified version of formula f1.4.4.6, from Bradie (2006).

    The survey writes the source's function as ``tan(pi*x) - x - 6``; the published intervals are `(0.40, 0.48)`; `[0,
    0.48]` (§2.4, p. 100); `[0, 0.5]` (Fig. 2.3).

    The second standard test problem: infinitely many roots; the smallest positive one is `0.4510472588`. `tan(pi*x)`
    has a pole at `x = 0.5`, the right bound of Fig. 2.3's interval. Bisection and false position on `(0.40, 0.48)` (Ex.
    2.2, Tables 2.2, 2.3, p. 74; Aitken on the false-position sequence in 2.6-3). Newton from `p0 = 0.48` converges in 5
    iterations; from `p0 = 0.4` it does not converge in 5000; from `p0 = 0` it converges to the root `697.4995475` (p.
    98). Secant from `p0 = 0.4, p1 = 0.48` (p. 109) and from `(0, 0.48)`, `(0.24, 0.48)`, `(0.4, 0.48)` (2.5-15). 2.1-13
    seeks the next smallest positive root.

    The formula holds only the test problem on ``[0, 0.5]``. It changes that interval to ``[0, 0.495]``: its upper bound
    moves left of the pole of ``tan(pi*x)`` at 0.5 by 1% of the published interval's width, rounded half up to 1
    significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[0, 0.5]`` does not satisfy the benchmark suite inclusion conditions, because
    ``b = 0.5`` is the pole: ``f(b)`` is about ``1.6e16`` in float64, and a shift along x by any ``c < 0`` crosses the
    pole.
    """

    number = (1, 99, 4, 4, 6)
    name = "Ex. 2.2"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location=(
            "Ex. 2.2; Fig. 2.3; Tables 2.2, 2.3, 2.5; §2.2 (p. 74); §2.4 (pp. 98, 100); §2.5 (p. 109); "
            "2.1-13; 2.5-15; 2.6-3"
        ),
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.495 * c
        return math.tan(math.pi * x) - x - 6

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.495)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.1485, c=0.25, expected=-5.946838507380154),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 0.495)),
    )
