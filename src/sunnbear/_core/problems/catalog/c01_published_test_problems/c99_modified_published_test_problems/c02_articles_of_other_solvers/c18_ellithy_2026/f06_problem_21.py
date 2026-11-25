"""This module holds formula f1.99.2.18.6, the modified version of the published formula f1.2.18.6.

A change of formula f1.2.18.6 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedEllithy2026Problem21(Formula):
    """This formula is the modified version of formula f1.2.18.6, from Ellithy (2026).

    The survey writes the source's function as ``(x^2 - 4)*(x + 1.5)*(x - 0.5)``; the published interval is ``[0, 2]``.

    The formula changes the published interval ``[0, 2]`` to ``[0, 1.98]``: its upper bound moves left of the root at 2
    by 1% of the published interval's width, rounded half up to 1 significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(b)`` is 0 at the
    root ``b = 2``.
    """

    number = (1, 99, 2, 18, 6)
    name = "Problem 21"
    params = ()
    location_in_publication = "dataset.json, problem 21"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\left(\tmp{u}^{2} - 4\right) \left(\tmp{u} + 1.5\right) \left(\tmp{u} - 0.5\right)",
        interval="[0, 1.98]",
        summary=(
            "A quartic that dips below 0 between a simple root inside the interval and a second root above the upper "
            "bound."
        ),
        notes=(
            (
                "The interval ends at 1.98, not at the published 2, which is a root, so that the function "
                "is not 0 there."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x**2 - 4) * (x + 1.5) * (x - 0.5)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.98)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.594, c=0.495, expected=2.558511608601),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.98)),
    )
