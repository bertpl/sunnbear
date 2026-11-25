"""This module holds formula f1.99.4.5.11, the modified version of the published formula f1.4.5.11.

A change of formula f1.4.5.11 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedEpperson2013Exercise3114B(Formula):
    """This formula is the modified version of formula f1.4.5.11, from Epperson (2013).

    The survey writes the source's function as ``1/(x - 1)``; the published interval is ``[0, 3]``.

    No root: a pole at `x = 1`, as in exercise 3.1-14(a).

    The formula returns 0 where ``x - c_scale*c`` equals 1, the only point at which the published function divides by 0;
    everywhere else it is the published function.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because it raises
    `ZeroDivisionError` at its pole, where a solver's evaluation can land.
    """

    number = (1, 99, 4, 5, 11)
    name = "Exercise 3.1-14(b)"
    params = ()
    location_in_publication = "Exercise 3.1-14(b)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\begin{cases} 0 & \text{if } \tmp{u} = 1 \\ \frac{1}{\tmp{u} - 1} & \text{otherwise} " r"\end{cases}"
        ),
        interval="[0, 3]",
        summary=r"A hyperbola that changes sign only at the pole, jumping from $-\infty$ to $+\infty$.",
        notes=(
            (
                r"The expression is 0 at the pole, $\tmp{u} = 1$ in float64, where the published function "
                "divides by 0."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate f at ``x - c_scale*c``, with 0 at the pole; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        if x == 1:
            return 0.0
        else:
            return 1 / (x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.75, expected=-1.1764705882352942),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
