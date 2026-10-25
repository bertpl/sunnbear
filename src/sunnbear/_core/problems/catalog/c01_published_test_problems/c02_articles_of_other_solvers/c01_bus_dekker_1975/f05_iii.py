"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``III`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class BusDekker1975Iii(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``x^n``, with the parameters ``n = 3, 5, 7, 9, 19, 25``; the formula's
    interval is ``[-1, 10]``.

    Group III: a zero of multiplicity `n` at 0.

    Only the test problem with ``n = 25`` has a version with ``modified = 1``, which adds ``TINY_LINEAR_TERM_SLOPE*x``
    to the published function, on the published interval; ``c`` shifts x as category 1 states, before the formula adds
    the term. `sunnbear._core.utils.floats` defines `TINY_LINEAR_TERM_SLOPE`.

    The published test problem with ``n = 25`` does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    ``x**25`` underflows to exactly 0 where ``abs(x)`` is below about 1.1e-13, and no form of ``x**25`` avoids the
    underflow. With the term, f is exactly 0 only within about 5e-48 of the root, and the term changes f by more than
    rounding only within about 1.4e-11 of the root.

    For the other published values of ``n``, up to 19, ``x**n`` underflows only within about 1e-17 of the root, and
    bisection lands on no exact 0.
    """

    number = (1, 2, 1, 5)
    name = "III"
    param_names = ("n", "modified")
    source = FormulaSource(
        reference=(
            "Bus, J. C. P., Dekker, T. J. (1975). Two efficient algorithms with guaranteed convergence "
            "for finding a zero of a function. ACM Transactions on Mathematical Software 1(4), 330–345."
            " https://doi.org/10.1145/355656.355659."
        ),
        location="III",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, add ``TINY_LINEAR_TERM_SLOPE*y``, with ``y = x - c_scale*c``. Category 1 states the rule
        for ``c_scale``.
        """
        x = x - 11.0 * c
        published_value = x**n
        if modified == 1:
            return published_value + TINY_LINEAR_TERM_SLOPE * x
        else:
            return published_value

    def interval_bounds(self, n: float, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(
                names=("n", "modified"), rows=((3.0, 0.0), (5.0, 0.0), (7.0, 0.0), (9.0, 0.0), (19.0, 0.0), (25.0, 0.0))
            ),
            ParamTable(names=("n", "modified"), rows=((25.0, 1.0),)),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={"n": 3.0, "modified": 0.0}, x=2.3, c=0.0, expected=12.166999999999998),
        FormulaTestCase.value(params={"n": 3.0, "modified": 0.0}, x=2.3, c=0.25, expected=-0.09112500000000011),
        FormulaTestCase.value(params={"n": 5.0, "modified": 0.0}, x=2.3, c=0.0, expected=64.36342999999998),
        FormulaTestCase.value(params={"n": 7.0, "modified": 0.0}, x=2.3, c=0.0, expected=340.48254469999983),
        FormulaTestCase.value(params={"n": 9.0, "modified": 0.0}, x=2.3, c=0.0, expected=1801.1526614629988),
        FormulaTestCase.value(params={"n": 19.0, "modified": 0.0}, x=2.3, c=0.0, expected=7461547.09275906),
        FormulaTestCase.value(params={"n": 25.0, "modified": 0.0}, x=2.3, c=0.0, expected=1104576757.1919525),
        FormulaTestCase.interval_bounds(params={"n": 3.0, "modified": 0.0}, expected=(-1.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"n": 25.0, "modified": 1.0}, expected=(-1.0, 10.0)),
        FormulaTestCase.value(params={"n": 25.0, "modified": 1.0}, x=2.3, c=0.25, expected=-2.1395027270670523e-09),
        FormulaTestCase.value(
            params={"n": 25.0, "modified": 1.0}, x=1e-14, c=0.0, expected=4.512985939662074e-291, atol=0.0
        ),
    )
