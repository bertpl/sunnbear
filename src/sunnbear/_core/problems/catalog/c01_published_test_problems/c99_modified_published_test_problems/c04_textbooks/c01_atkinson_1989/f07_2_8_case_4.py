"""This module holds formula f1.99.4.1.7, the modified version of the published formula f1.4.1.7.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.1.7 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class ModifiedAtkinson198928Case4(Formula):
    """This formula is the modified version of formula f1.4.1.7, from Atkinson (1989).

    The survey writes the source's function as ``(x - 1)*exp(-1/(x - 1)^2)``; the published interval is ``[0, 3]``.

    Root 1 of infinite multiplicity: every derivative vanishes there. Brent's algorithm stops at 0.9277553, where the
    computed ``f`` is 0 (Table 2.15).

    At its root ``x = 1``, where the expression divides by 0, the formula takes its limit 0.

    The formula adds ``TINY_LINEAR_TERM_SLOPE*(x - 1)`` to the published function, on the published interval; ``c``
    shifts x by the rule of category 1, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is about 4.5e-277.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    In float64, the published function is exactly 0 within about 0.04 of the root, because its true values there lie
    below float64's range; no way of writing the function avoids these exact zeros.

    With the term, f is exactly 0 only within about 5e-48 of the root, where the term underflows too; beyond about 0.04
    from the root, the term changes f by less than the rounding error of f.

    The modification changes what the test problem tests: with the published function, a solver may stop at any x-value
    within about 0.04 of the root, while with the term a solver must locate the root, near which f is the linear term.
    """

    number = (1, 99, 4, 1, 7)
    name = "§2.8 case (4)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="§2.8 case (4); P34(iv)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, and add ``TINY_LINEAR_TERM_SLOPE*(y - 1)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 3.0 * c
        if x == 1.0:
            # at its root x = 1, the expression divides by 0; the formula takes its limit 0
            published_value = 0.0
        else:
            published_value = (x - 1.0) * math.exp(-1.0 / (x - 1.0) ** 2)
        return published_value + TINY_LINEAR_TERM_SLOPE * (x - 1.0)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-0.21297042461623097),
        FormulaTestCase.value(params={}, x=0.9999, c=0.0, expected=-4.512985939661577e-281, atol=0.0),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=0.0, atol=0.0),
    )
