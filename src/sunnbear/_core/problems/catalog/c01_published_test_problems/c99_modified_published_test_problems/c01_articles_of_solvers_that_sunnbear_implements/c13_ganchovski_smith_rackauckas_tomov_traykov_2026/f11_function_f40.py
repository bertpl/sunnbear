"""This module holds formula f1.99.1.13.11, the modified version of the published formula f1.1.13.11.

A change of formula f1.1.13.11 may need a matching change of this module.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class ModifiedGanchovskiSmithRackauckasTomovTraykov2026FunctionF40(Formula):
    """This formula is the modified version of formula f1.1.13.11, from Ganchovski et al. (2026).

    The survey writes the source's function as ``if(x = 0; 0.0; 1/(x - 2/3))``; the published interval is ``[-11, 9]``.

    The formula returns 0 where ``x - c_scale*c`` equals 0, as the published function does at ``x = 0``, and also where
    ``x - c_scale*c`` equals the float of 2/3, the only point at which the published function divides by 0; everywhere
    else it is the published function.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because it raises
    `ZeroDivisionError` at its pole, where a solver's evaluation can land.
    """

    number = (1, 99, 1, 13, 11)
    name = "Function f40"
    params = ()
    location_in_publication = "Table 2, f40"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=(
            r"\begin{cases} 0 & \text{if } \tmp{u} = 0 \text{ or } \tmp{u} = \frac{2}{3} \\ "
            r"\frac{1}{\tmp{u} - \frac{2}{3}} & \text{otherwise} \end{cases}"
        ),
        interval="[-11, 9]",
        summary=r"A hyperbola that changes sign only at its pole, with the value set to 0 at $\x = 20 \c$.",
        notes=(
            (
                r"The expression is 0 at the pole, $\tmp{u} = 2/3$ in float64, where the published "
                "function divides by 0."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate f at ``x - c_scale*c``, with 0 at the pole; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        if x == 0 or x == 2 / 3:
            return 0.0
        else:
            return 1 / (x - 2 / 3)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-11.0, 9.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-5.0, c=0.25, expected=-0.09375),
        FormulaTestCase.value(params={}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={}, x=0.6666666666666666, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-11.0, 9.0)),
    )
