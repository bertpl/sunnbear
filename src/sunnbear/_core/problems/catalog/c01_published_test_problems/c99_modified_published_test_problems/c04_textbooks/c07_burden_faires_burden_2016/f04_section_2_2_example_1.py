"""This module holds formula f1.99.4.7.4, the modified version of the published formula f1.4.7.4.

A change of formula f1.4.7.4 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedBurdenFairesBurden2016Section22Example1(Formula):
    """This formula is the modified version of formula f1.4.7.4, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = x^2 - 2``; the published interval is `[-3, 3]` (Fig. 2.2).

    Fixed points -1 and 2, from `(p + 1)*(p - 2) = 0`.

    The formula changes the published interval ``[-3, 3]`` to ``[-3, 1]``: the upper bound moves left of the second
    root at 2, so that the interval holds 1 of the 2 roots; ``c`` shifts x by the rule of category 1, with ``c_scale``
    the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 7, 4)
    name = "Section 2.2, example 1"
    params = ()
    location_in_publication = "§2.2 Example 1; Fig. 2.2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 10 \c"),),
        expression=r"\tmp{u} - \left(\tmp{u}^{2} - 2\right)",
        interval="[-3, 1]",
        summary="A concave parabola with 1 simple root on the interval and the vertex 1.5 to the right of that root.",
        notes=(
            (
                "The interval ends at 1, not at the published 3, so that it holds 1 of the published "
                "interval's 2 roots: with an even number of roots, the function has the same sign at both "
                "published bounds."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 10.0 * c
        return (x) - (x**2 - 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.8, c=0.1, expected=-8.639999999999999),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 1.0)),
    )
