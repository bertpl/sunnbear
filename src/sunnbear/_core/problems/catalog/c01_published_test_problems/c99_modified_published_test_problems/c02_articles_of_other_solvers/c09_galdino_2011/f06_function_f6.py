"""This module holds formula f1.99.2.9.6, the modified version of the published formula f1.2.9.6.

A change of formula f1.2.9.6 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedGaldino2011FunctionF6(Formula):
    """This formula is the modified version of formula f1.2.9.6, from Galdino (2011).

    The survey writes the source's function as ``exp((x - 3)^5) - 1``; the published interval is ``[2.5, 3.5]``.

    The appendix states a zero of multiplicity 5 at `x = 3`, under the label `f7`.

    The formula computes the published function in the equivalent form ``expm1((x - 3)**5)``, on the published interval;
    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``exp((x - 3)**5)`` rounds to 1, and the subtraction of 1 cancels, so that f is exactly 0 at many
    x-values within about 7e-4 of the root; ``expm1(u)`` computes ``exp(u) - 1`` without the subtraction.
    """

    number = (1, 99, 2, 9, 6)
    name = "Function f6"
    params = ()
    location_in_publication = "Table IV, f6"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\operatorname{expm1}\left(\left(\tmp{u} - 3\right)^{5}\right)",
        interval="[2.5, 3.5]",
        summary="A function that stays below $10^{-4}$ in magnitude within 0.15 of its root of multiplicity 5.",
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
        x = x - 1.0 * c
        return math.expm1((x - 3) ** 5)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.5, 3.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(2.5, 3.5)),
        FormulaTestCase.value(params={}, x=2.8, c=0.25, expected=-0.018283601758623744),
    )
