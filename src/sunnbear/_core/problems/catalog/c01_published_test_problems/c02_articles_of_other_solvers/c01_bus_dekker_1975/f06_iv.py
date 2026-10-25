"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``IV`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so the module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write it.

Nor does the generator write a formula with the parameter ``modified``, which selects a modified version of a published
test problem. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class BusDekker1975Iv(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``0`` if ``x = 0``; ``x*exp(-x^-2)`` otherwise; the formula's interval is
    ``[-1, 4]``.

    Group IV: all derivatives vanish at the zero, which the article calls a multiplicity of infinity.

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

    number = (1, 2, 1, 6)
    name = "IV"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Bus, J. C. P., Dekker, T. J. (1975). Two efficient algorithms with guaranteed convergence "
            "for finding a zero of a function. ACM Transactions on Mathematical Software 1(4), 330–345."
            " https://doi.org/10.1145/355656.355659."
        ),
        location="IV",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, add ``TINY_LINEAR_TERM_SLOPE*y``, with ``y = x - c_scale*c``. Category 1 states the rule
        for ``c_scale``.
        """
        x = x - 5.0 * c
        # below 1e-100, float64 rounds x*exp(-x^-2) to 0, and x**-2 overflows
        if abs(x) < 1e-100:
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
        FormulaTestCase.value(params={"modified": 0.0}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={"modified": 0.0}, x=1e-200, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.01, c=0.0, expected=4.512985939662074e-279, atol=0.0),
    )
