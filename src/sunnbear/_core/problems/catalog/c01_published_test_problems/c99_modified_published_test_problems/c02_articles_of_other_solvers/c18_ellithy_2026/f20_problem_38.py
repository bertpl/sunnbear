"""This module holds formula f1.99.2.18.20, the modified version of the published formula f1.2.18.20.

A change of formula f1.2.18.20 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedEllithy2026Problem38(Formula):
    """This formula is the modified version of formula f1.2.18.20, from Ellithy (2026).

    The survey writes the source's function as ``x^4 + 2*x^3 - 13*x^2 - 14*x + 24``; the published interval is ``[-3,
    1]``.

    The formula changes the published interval ``[-3, 1]`` to ``[-3, 0.96]``: its upper bound moves left of the root at
    1 by 1% of the published interval's width, rounded half up to 1 significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(b)`` is 0 at the
    root ``b = 1``.
    """

    number = (1, 99, 2, 18, 20)
    name = "Problem 38"
    params = ()
    location_in_publication = "dataset.json, problem 38"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 3.96 \c"),),
        expression=r"\tmp{u}^{4} + 2 \tmp{u}^{3} - 13 \tmp{u}^{2} - 14 \tmp{u} + 24",
        interval="[-3, 0.96]",
        summary=(
            r"The quartic $(\tmp{u} + 4)(\tmp{u} + 2)(\tmp{u} - 1)(\tmp{u} - 3)$ written out as a polynomial, with 1 of"
            r" its 4 roots on the interval."
        ),
        notes=(
            (
                "The interval ends at 0.96, not at the published 1, which is a root, so that the function "
                "is not 0 there."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.96 * c
        return x**4 + 2 * x**3 - 13 * x**2 - 14 * x + 24

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 0.96)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.812, c=0.25, expected=-21.194394966384),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 0.96)),
    )
