"""This module holds a formula of Brent (1973).

The formula comes from the row with the key ``(4.1)`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so the module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write it.

Nor does the generator write a formula with the parameter ``modified``, which selects a modified version of a published
test problem. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class Brent197341(Formula):
    """This formula comes from Brent (1973).

    The survey writes the source's function as ``0`` if ``abs(x) < 3.8*10^-4``; ``fl(x*exp(-x^-2))`` otherwise. The
    source names it ``f_1``. The formula's interval is ``[-1.0, +4.0]``, on which the book's procedure ``zero2`` solves
    with the absolute tolerance ``t = 1E-20``.

    ``fl(.)`` is the computed floating-point value. Table 4.1's footnote: ``zero2`` returned ``2.17E-4``, where ``f_1 =
    0``.

    In float64, ``x*exp(-x^-2)`` underflows to 0 for ``abs(x)`` below about 0.0367, so the formula is 0 on about
    ``[-0.0367, 0.0367]``. The book's procedure ``zero2`` represents each function value as ``y*2^z`` and does not
    underflow, so its ``f_1`` is 0 only for ``abs(x) < 3.8*10^-4``.

    With ``modified = 1``, the formula adds ``TINY_LINEAR_TERM_SLOPE*x`` to the published function, on the published
    interval; ``c`` shifts x as category 1 states, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is
    ``2**-918``.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    In float64, the published function is exactly 0 within about 0.04 of the root, because its true values there lie
    below float64's range, so that no form of it avoids the zeros. With the term, f is exactly 0 only within about 5e-48
    of the root, where the term underflows too; beyond about 0.04 from the root, the term changes f by less than its
    rounding.

    With ``modified = 1``, the modification changes what the test problem tests: in float64, the published function is
    exactly 0 within about 0.04 of the root, so that a solver may stop at any x-value there, while with the term a
    solver must locate the root, near which f is the linear term.
    """

    number = (1, 1, 4, 3)
    name = "(4.1)"
    param_names = ("modified",)
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
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, add ``TINY_LINEAR_TERM_SLOPE*y``, with ``y = x - c_scale*c``. Category 1 states the rule
        for ``c_scale``.
        """
        x = x - 5.0 * c
        if abs(x) < 3.8e-4:
            published_value = 0.0
        else:
            published_value = x * math.exp(-(x**-2))
        if modified == 1:
            return published_value + TINY_LINEAR_TERM_SLOPE * x
        else:
            return published_value

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.0001, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.0001, c=0.0, expected=4.512985939662074e-281, atol=0.0),
    )
