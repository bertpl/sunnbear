"""This module holds formula f1.99.2.1.5, the modified version of the published formula f1.2.1.5.

A change of formula f1.2.1.5 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class ModifiedBusDekker1975GroupIii(Formula):
    """This formula is the modified version of formula f1.2.1.5, from Bus, Dekker (1975).

    The survey writes the source's function as ``x^n``, with the parameters ``n = 3, 5, 7, 9, 19, 25``; the published
    interval is ``[-1, 10]``.

    Group III: a zero of multiplicity `n` at 0.

    The formula holds only the test problem with ``n = 25``. The formula adds ``TINY_LINEAR_TERM_SLOPE*x`` to the
    published function, on the published interval; ``c`` shifts x by the rule of category 1, before the formula adds the
    term. `TINY_LINEAR_TERM_SLOPE` is about 4.5e-277.

    The published test problem with ``n = 25`` does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    ``x**25`` underflows to exactly 0 where ``abs(x)`` is below about 1.1e-13, and no form of ``x**25`` avoids the
    underflow. With the term, f is exactly 0 only within about 5e-48 of the root, and the term changes f by more than
    the rounding error of f only within about 1.4e-11 of the root, closer to the root than the smallest ``xtol`` that
    the benchmark uses for this test problem, about 2e-11.

    For the other published values of ``n``, up to 19, ``x**n`` underflows only within about 1e-17 of the root, and
    bisection lands on no exact 0.
    """

    number = (1, 99, 2, 1, 5)
    name = "Group III"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Group III"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u}^{\param{n}} + 2^{-918} \, \tmp{u}",
        interval="[-1, 10]",
        summary="A function antisymmetric about its root, below 0.01 in magnitude within 0.83 of that root.",
        notes=(
            (
                r"The term $2^{-918} \, \tmp{u}$ keeps the function from being exactly 0 within about "
                r"$10^{-13}$ of its root, where $\tmp{u}^{\param{n}}$ underflows to 0 in float64 at "
                r"$\param{n} = 25$."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, and add ``TINY_LINEAR_TERM_SLOPE*y``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 10.0 * c
        published_value = x**n
        return published_value + TINY_LINEAR_TERM_SLOPE * x

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter value of the modified test problem."""
        return (ParamTable(names=("n",), rows=((25.0,),), summary="The published parameter value $\\param{n} = 25$."),)

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={"n": 25.0}, expected=(-1.0, 10.0)),
        FormulaTestCase.value(params={"n": 25.0}, x=2.3, c=0.275, expected=-2.1395027270670523e-09),
        FormulaTestCase.value(params={"n": 25.0}, x=1e-14, c=0.0, expected=4.512985939662074e-291, atol=0.0),
    )
