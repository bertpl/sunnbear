"""This module holds formula f1.99.4.3.15, the modified version of the published formula f1.4.3.15.

A change of formula f1.4.3.15 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import bessel_j0, bessel_y0


class ModifiedMoler2004Exercise410C(Formula):
    """This formula is the modified version of formula f1.4.3.15, from Moler (2004).

    The survey writes the source's function as ``J0(x) = Y0(x)``; the published interval is ``[0, 10*pi]``.

    All solutions between 0 and `10*pi`.

    The formula changes the published interval ``[0, 10*pi]`` to ``[2, 10*pi]``: its lower bound moves right of the
    first root, near 1.64, so that ``f(a)`` is finite and the interval holds 9 of the 10 roots.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` is not
    finite, since ``bessel_y0(0)`` is ``-inf``, and the published interval holds 10 roots, an even number.

    The modification changes what the test problem tests: Ex. 4.10(c) asks for all solutions between 0 and ``10*pi``,
    and a solver on ``[2, 10*pi]`` finds 1 of the 9 solutions in that interval.
    """

    number = (1, 99, 4, 3, 15)
    name = "Exercise 4.10(c)"
    params = ()
    location_in_publication = "Exercise 4.10(c)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 29.4 \c"),),
        expression=r"J_{0}\left(\tmp{u}\right) - Y_{0}\left(\tmp{u}\right)",
        interval=r"[2, 10 \pi]",
        notes=(
            (
                "The interval starts at 2, not at the published 0, where $Y_0$ is not finite, so that it "
                "holds 9 of the published interval's 10 roots: with an even number of roots, the function "
                "has the same sign at both published bounds."
            ),
            (
                "This changes what the test problem tests: the source asks for all the solutions between "
                r"0 and $10\pi$, and a solver on the modified interval finds 1 of them."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 29.4 * c
        return (bessel_j0(x)) - (bessel_y0(x))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 31.41592653589793)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=10.8248, c=0.25, expected=-0.575867514061962),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 31.41592653589793)),
    )
