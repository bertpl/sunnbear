"""This module holds formula f1.99.4.3.6, the modified version of the published formula f1.4.3.6.

A change of formula f1.4.3.6 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedMoler2004Section410(Formula):
    """This formula is the modified version of formula f1.4.3.6, from Moler (2004).

    The survey writes the source's function as ``1/((x - 0.3)^2 + 0.01) + 1/((x - 0.9)^2 + 0.04) - 6``; the published
    interval is `[-1, 2]` (Figure 4.8).

    MATLAB's demo function `humps`, which §4.10 says illustrates graphics, quadrature and zero-finding routines; §4.7
    names the handle `@humps` as an example of syntax. The chapter uses it only for minimization: `fmintx` minimizes
    `-humps(x)` on `[-1, 2]` (§4.10, Figure 4.8; Ex. 4.17).

    The formula changes the published interval ``[-1, 2]`` to ``[-1, 1]``: its upper bound moves left of the second
    root, near 1.3, so that the interval holds 1 of the 2 roots. ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 3, 6)
    name = "Section 4.10"
    params = ()
    location_in_publication = "§4.7, §4.10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\frac{1}{\left(\tmp{u} - 0.3\right)^{2} + 0.01} + \frac{1}{\left(\tmp{u} - " r"0.9\right)^{2} + 0.04} - 6"
        ),
        interval="[-1, 1]",
        summary=(
            "A function with 1 simple root on the interval and 2 steep peaks to the right of that root, referred to in "
            'the source as "humps".'
        ),
        notes=(
            (
                "The interval ends at 1, not at the published 2, so that it holds 1 of the published "
                "interval's 2 roots: with an even number of roots, the function has the same sign at both "
                "published bounds."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 1 / ((x - 0.3) ** 2 + 0.01) + 1 / ((x - 0.9) ** 2 + 0.04) - 6

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.5, expected=-5.005466778805719),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
