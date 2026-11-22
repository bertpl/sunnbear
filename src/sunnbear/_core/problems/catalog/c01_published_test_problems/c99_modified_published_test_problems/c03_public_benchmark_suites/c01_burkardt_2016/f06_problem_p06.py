"""This module holds formula f1.99.3.1.6, the modified version of the published formula f1.3.1.6.

A change of formula f1.3.1.6 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedBurkardt2016ProblemP06(Formula):
    """This formula is the modified version of formula f1.3.1.6, from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 2.0 - 1.0/(10.0*x)^2 + 2.0/(100.0*x)^3``; the published
    intervals are `[0.00001, 20.0]` (rang); `[0.0002, 2.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.0002` and `2.0`. The title has `- 2 / ( 100 * X )^3` where the code
    and the docstring have `+`. The function does not change sign on `rang`, `[0.00001, 20.0]`, which holds 2 roots,
    about `0.0001999992` and `0.7032048404`; `p06_root` returns only the 2nd, `0.7032048403631358`.

    The formula holds only the test problem on ``[1e-05, 20]``. The formula changes that interval to ``[0.08, 20]``: its
    lower bound moves right of the first root, near 0.00019, so that the interval holds 1 of the 2 roots.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[1e-05, 20]`` does not satisfy the benchmark suite inclusion conditions, because
    the published interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 3, 1, 6)
    name = "Problem p06"
    params = ()
    location_in_publication = "Problem p06"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 19.9 \c"),),
        expression=(
            r"e^{\tmp{u}} - 2.0 - \frac{1.0}{\left(10.0 \tmp{u}\right)^{2}} + \frac{2.0}{\left(100.0 "
            r"\tmp{u}\right)^{3}}"
        ),
        interval="[0.08, 20]",
        notes=(
            (
                "The interval starts at 0.08, not at the published $10^{-5}$, so that it holds 1 of the "
                "published interval's 2 roots: with an even number of roots, the function has the same "
                "sign at both published bounds."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 19.9 * c
        return math.exp(x) - 2.0 - 1.0 / (10.0 * x) ** 2 + 2.0 / (100.0 * x) ** 3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.08, 20.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=6.056, c=0.25, expected=0.9390697531278249),
        FormulaTestCase.interval_bounds(params={}, expected=(0.08, 20.0)),
    )
