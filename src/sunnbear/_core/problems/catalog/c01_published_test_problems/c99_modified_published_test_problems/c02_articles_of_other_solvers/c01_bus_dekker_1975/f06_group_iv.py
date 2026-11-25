"""This module holds formula f1.99.2.1.6, the modified version of the published formula f1.2.1.6.

A change of formula f1.2.1.6 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class ModifiedBusDekker1975GroupIv(Formula):
    """This formula is the modified version of formula f1.2.1.6, from Bus, Dekker (1975).

    The survey writes the source's function as ``0`` if ``x = 0``; ``x*exp(-x^-2)`` otherwise; the published interval is
    ``[-1, 4]``.

    Group IV: all derivatives vanish at the zero, which the article calls a multiplicity of infinity.

    The formula adds ``TINY_LINEAR_TERM_SLOPE*x`` to the published function, on the published interval; ``c`` shifts x
    by the rule of category 1, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is about 4.5e-277.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    In float64, the published function is exactly 0 within about 0.04 of the root, because its true values there lie
    below float64's range; no way of writing the function avoids these exact zeros.

    With the term, f is exactly 0 only within about 5e-48 of the root, where the term underflows too; beyond about 0.04
    from the root, the term changes f by less than the rounding error of f.

    The modification changes what the test problem tests: with the published function, a solver may stop at any x-value
    within about 0.04 of the root, while with the term a solver must locate the root, near which f is the linear term.
    """

    number = (1, 99, 2, 1, 6)
    name = "Group IV"
    params = ()
    location_in_publication = "Group IV"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - 10 \c"),
            (
                r"\fn{g}(\x)",
                (
                    r"\begin{cases} 0 & \text{if } |\x| < 10^{-100} \\ \x e^{-\x^{-2}} & \text{otherwise} "
                    r"\end{cases}"
                ),
            ),
        ),
        expression=r"\fn{g}(\tmp{u}) + 2^{-918} \, \tmp{u}",
        interval="[-1, 4]",
        summary=(
            "A function so flat at its root that the function stays below $10^{-270}$ in magnitude on a band 0.08 wide "
            "around that root."
        ),
        notes=(
            (
                r"$\fn{g}(\x)$ is 0 for $|\x| < 10^{-100}$, where float64 rounds $\x e^{-\x^{-2}}$ to 0 "
                r"anyway; the published function is 0 only at $\x = 0$."
            ),
            (
                r"The term $2^{-918} \, \tmp{u}$ keeps the function from being exactly 0 within about 0.04 "
                r"of its root, where the published function, $\fn{g}(\tmp{u})$, underflows to 0 in "
                "float64. This changes what the test problem tests: with the published function, a solver "
                "may stop at any x-value within about 0.04 of the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, and add ``TINY_LINEAR_TERM_SLOPE*y``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 10.0 * c
        # below 1e-100, float64 rounds x*exp(-x^-2) to 0, and x**-2 overflows
        if abs(x) < 1e-100:
            published_value = 0.0
        else:
            published_value = x * math.exp(-(x**-2))
        return published_value + TINY_LINEAR_TERM_SLOPE * x

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 4.0)),
        FormulaTestCase.value(params={}, x=0.5, c=0.125, expected=-0.12675998655454956),
        FormulaTestCase.value(params={}, x=0.01, c=0.0, expected=4.512985939662074e-279, atol=0.0),
        FormulaTestCase.value(params={}, x=0.0, c=0.0, expected=0.0, atol=0.0),
    )
