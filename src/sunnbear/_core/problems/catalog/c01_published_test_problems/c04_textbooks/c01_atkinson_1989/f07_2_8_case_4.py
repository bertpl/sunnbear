"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``§2.8 case (4); P34(iv)`` in the survey of published test problems. The
survey gives this function as 1 expression that the module generator,
`scripts/literature_test_problems/formula_modules.py`, cannot translate: a removable singularity at its root `x = 1`,
where the expression divides by 0 and the formula needs the limit 0.

Nor does the generator write a formula with the parameter ``modified``, which selects a modified version of a published
test problem. A person therefore writes this module, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class Atkinson198928Case4(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``(x - 1)*exp(-1/(x - 1)^2)``; the formula's interval is ``[0, 3]``.

    Root 1 of infinite multiplicity: every derivative vanishes there. Brent's algorithm stops at 0.9277553, where the
    computed ``f`` is 0 (Table 2.15).

    At its root ``x = 1``, where the expression divides by 0, the formula takes its limit 0.

    With ``modified = 1``, the formula adds ``TINY_LINEAR_TERM_SLOPE*(x - 1)`` to the published function, on the
    published interval; ``c`` shifts x as category 1 states, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE`
    is ``2**-918``.

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

    number = (1, 4, 1, 7)
    name = "§2.8 case (4)"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="§2.8 case (4); P34(iv)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, add ``TINY_LINEAR_TERM_SLOPE*(y - 1)``, with ``y = x - c_scale*c``. Category 1 states the
        rule for ``c_scale``.
        """
        x = x - 3.0 * c
        if x == 1.0:
            # at its root x = 1, the expression divides by 0; the formula takes its limit 0
            published_value = 0.0
        else:
            published_value = (x - 1.0) * math.exp(-1.0 / (x - 1.0) ** 2)
        if modified == 1:
            return published_value + TINY_LINEAR_TERM_SLOPE * (x - 1.0)
        else:
            return published_value

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=0.9, c=0.0, expected=-3.72007597602067e-45),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.9, c=0.25, expected=-0.21297042461623097),
        FormulaTestCase.value(params={"modified": 0.0}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(0.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(0.0, 3.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.9, c=0.25, expected=-0.21297042461623097),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.9999, c=0.0, expected=-4.512985939661577e-281, atol=0.0),
    )
