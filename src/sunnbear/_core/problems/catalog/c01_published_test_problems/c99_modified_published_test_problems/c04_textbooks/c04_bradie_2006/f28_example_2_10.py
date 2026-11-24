"""This module holds formula f1.99.4.4.28, the modified version of the published formula f1.4.4.28.

A change of formula f1.4.4.28 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedBradie2006Example210(Formula):
    """This formula is the modified version of formula f1.4.4.28, from Bradie (2006).

    The survey writes the source's function as ``x*(1 - cos(x))``; the published interval is `[-2, 1]` (Ex. 2.10).

    Root 0 of multiplicity 3. Newton from `p0 = 1` converges linearly, at rate 2/3, and bisection on `[-2, 1]` beats it
    (Ex. 2.10); secant from `p0 = -1, p1 = 2` (2.5-11); Aitken on the Newton sequence (2.6-4); both techniques for
    restoring quadratic convergence, from `p0 = 1` (2.6-12). 2.6-13 estimates the multiplicity 3 from the 2.6-4
    sequence.

    The formula computes the published function in the equivalent form ``2*x*sin(x/2)**2``, on the published interval;
    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``cos(x)`` rounds to 1, and ``1 - cos(x)`` cancels, so that f is exactly 0 at many x-values within
    about 1e-8 of the root; ``2*x*sin(x/2)**2`` has no subtraction.
    """

    number = (1, 99, 4, 4, 28)
    name = "Example 2.10"
    params = ()
    location_in_publication = "Example 2.10; Exercises 2.5-11(a), 2.6-4, 2.6-12, 2.6-13"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3 \c"),),
        expression=r"2 \tmp{u} \sin^{2}{\left(\frac{\tmp{u}}{2} \right)}",
        interval="[-2, 1]",
        summary=(
            "A function that is odd about its triple root and below $10^{-3}$ in magnitude on a band 0.25 wide around "
            "that root."
        ),
        notes=(
            (
                r"The expression equals the published function, $$\tmp{u} \left(1 - \cos{\left(\tmp{u} "
                r"\right)}\right),$$ without the cancellation that makes the published function exactly 0 "
                "at many x-values next to the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``2*y*sin(y/2)**2``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 3.0 * c
        return 2 * x * math.sin(x / 2) ** 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 1.0)),
        FormulaTestCase.value(params={}, x=-1.1, c=0.25, expected=-2.359841956625349),
    )
