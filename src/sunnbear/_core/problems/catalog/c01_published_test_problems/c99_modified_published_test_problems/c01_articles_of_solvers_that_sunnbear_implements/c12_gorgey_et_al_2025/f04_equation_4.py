"""This module holds formula f1.99.1.12.4, the modified version of the published formula f1.1.12.4.

A change of formula f1.1.12.4 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedGorgeyEtAl2025Equation4(Formula):
    """This formula is the modified version of formula f1.1.12.4, from Gorgey et al. (2025).

    The survey writes the source's function as ``exp((x - 3)^5) - 1``; the published interval is ``[2, 4]``.

    Root `3`.

    The formula computes the published function in the equivalent form ``expm1((x - 3)**5)``, on the published interval,
    and ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``exp((x - 3)**5)`` rounds to 1, and the subtraction of 1 cancels, so that f is exactly 0 at many
    x-values within about 7e-4 of the root; ``expm1(u)`` computes ``exp(u) - 1`` without the subtraction.
    """

    number = (1, 99, 1, 12, 4)
    name = "Equation 4"
    params = ()
    location_in_publication = "Equation 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\operatorname{expm1}\left(\left(\tmp{u} - 3\right)^{5}\right)",
        interval="[2, 4]",
        notes=(
            (
                r"$\operatorname{expm1}(z)$ is $e^z - 1$, computed without the cancellation that makes the "
                r"published function, $$e^{\left(\tmp{u} - 3\right)^{5}} - 1,$$ exactly 0 at many x-values "
                "next to the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``expm1((y - 3)**5)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 2.0 * c
        return math.expm1((x - 3) ** 5)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 4.0)),
        FormulaTestCase.value(params={}, x=2.6, c=0.25, expected=-0.4459442690988902),
    )
