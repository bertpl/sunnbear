"""This module holds a formula of Parida, Gupta (2006).

The formula comes from the row with the key ``1`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ParidaGupta2006Example1(Formula):
    """This formula comes from Parida, Gupta (2006).

    The survey writes the source's function as ``x^5 - 300*x^2 - 126*x + 5005``; the formula's interval is ``[-20,
    20]``.

    `x0 = -20`. The interval holds 3 roots: -3.909221, 5 and about 5.00105. Table 1 reports -3.909221 for all 3 methods.
    """

    number = (1, 2, 5, 1)
    name = "Example 1"
    params = ()
    location_in_publication = "Example 1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 40 \c"),),
        expression=r"\tmp{u}^{5} - 300 \tmp{u}^{2} - 126 \tmp{u} + 5005",
        interval="[-20, 20]",
        summary=(
            "A quintic with 3 simple roots, the upper 2 only about 0.001 apart, on either side of a minimum just below "
            "0."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 40.0 * c
        return x**5 - 300 * x**2 - 126 * x + 5005

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-20.0, 20.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-8.0, c=0.0, expected=-45955.0),
        FormulaTestCase.value(params={}, x=-8.0, c=0.25, expected=-1979495.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-20.0, 20.0)),
    )
