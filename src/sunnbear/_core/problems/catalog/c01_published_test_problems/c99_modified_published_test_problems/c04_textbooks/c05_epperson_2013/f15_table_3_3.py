"""This module holds formula f1.99.4.5.15, the modified version of the published formula f1.4.5.15.

A change of formula f1.4.5.15 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedEpperson2013Table33(Formula):
    """This formula is the modified version of formula f1.4.5.15, from Epperson (2013).

    The survey writes the source's function as ``(20*x - 1)/(19*x)``; the published intervals are `[0.01, 1]` (Table
    3.16); `[-0.2, 0.2]` (Fig. 3.4).

    Root 0.05. Table 3.3: the first Newton step from `x0 = 1, 0.5, 0.25, 0.125, 0.0625` gives `x1 < 0` until `x0 =
    1/16`. Table 3.16: the hybrid method (Algorithm 3.6), from `x0 = 0.01, x1 = 1`.

    The formula holds only the test problem on ``[-0.2, 0.2]``. It changes that interval to ``[0.01, 0.2]``: the lower
    bound moves right of the pole at 0, to the lower bound of the other published interval, so that the interval holds
    its root and no pole.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problem on ``[-0.2, 0.2]`` does not satisfy the benchmark suite inclusion conditions, because
    the pole at 0 is a second sign change, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 5, 15)
    name = "Table 3.3"
    params = ()
    location_in_publication = "§3.2 (p. 100), Fig. 3.4, Table 3.3; Example 3.19, Table 3.16"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.19 \c"),),
        expression=r"\frac{20 \tmp{u} - 1}{19 \tmp{u}}",
        interval="[0.01, 0.2]",
        summary=(
            "An increasing hyperbola with 1 simple root, steep next to the lower bound because of the hyperbola's pole "
            "below that bound."
        ),
        notes=(
            (
                "The interval starts at 0.01, the lower bound of the source's other interval, not at the "
                "published $-0.2$, so that it holds the root and not the pole at 0. The pole is a second "
                "sign change, so the function has the same sign at both published bounds."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.19 * c
        return (20 * x - 1) / (19 * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.01, 0.2)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.067, c=0.25, expected=-1.6464237516869091),
        FormulaTestCase.interval_bounds(params={}, expected=(0.01, 0.2)),
    )
