"""This module holds formula f1.99.1.4.3, the modified version of the published formula f1.1.4.3.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.4.3 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class ModifiedBrent197341(Formula):
    """This formula is the modified version of formula f1.1.4.3, from Brent (1973).

    The survey writes the source's function as ``0`` if ``abs(x) < 3.8*10^-4``; ``fl(x*exp(-x^-2))`` otherwise. The
    source names it ``f_1``. The published interval is ``[-1.0, +4.0]``, on which the book's procedure ``zero2`` solves
    with the absolute tolerance ``t = 1E-20``.

    ``fl(.)`` is the computed floating-point value. Table 4.1's footnote: ``zero2`` returned ``2.17E-4``, where
    ``f_1 = 0``.

    In float64, ``x*exp(-x^-2)`` underflows to 0 for ``abs(x)`` below about 0.0367, so the published function is 0 on
    about ``[-0.0367, 0.0367]``. The book's procedure ``zero2`` represents each function value as ``y*2^z`` and does not
    underflow, so its ``f_1`` is 0 only for ``abs(x) < 3.8*10^-4``.

    The formula adds ``TINY_LINEAR_TERM_SLOPE*x`` to the published function, on the published interval; ``c`` shifts x
    by the rule of category 1, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is about 4.5e-277.

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

    number = (1, 99, 1, 4, 3)
    name = "(4.1)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall, "
            "Englewood Cliffs, NJ. ISBN 0-13-022335-2. Author's scan: "
            "https://maths-people.anu.edu.au/~brent/pub/pub011.html. Erratum: Brent, R. P. (1975). "
            "Table Errata 520. Mathematics of Computation 29(132), 1166. "
            "https://doi.org/10.1090/s0025-5718-1975-0371062-9."
        ),
        location="(4.1)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, and add ``TINY_LINEAR_TERM_SLOPE*y``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 5.0 * c
        if abs(x) < 3.8e-4:
            published_value = 0.0
        else:
            published_value = x * math.exp(-(x**-2))
        return published_value + TINY_LINEAR_TERM_SLOPE * x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 4.0)),
        FormulaTestCase.value(params={}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={}, x=0.0001, c=0.0, expected=4.512985939662074e-281, atol=0.0),
    )
