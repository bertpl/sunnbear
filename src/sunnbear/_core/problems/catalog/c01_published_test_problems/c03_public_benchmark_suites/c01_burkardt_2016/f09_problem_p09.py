"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p09`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Burkardt2016ProblemP09(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``0.75*(x - 6.25) - 0.3125`` (x < 6.0); ``2.00*(x - 6.25)`` (6.0 <= x <=
    6.50); ``0.75*(x - 6.25) + 0.3125`` (x > 6.50); the formula's intervals are ``[-5.0, 16.0]`` (rang); ``[6.25 - 1.0,
    6.25 + 5.0]`` (starts 2 and 1).

    The source's starting points, in order, are ``6.25 + 5.0``, ``6.25 - 1.0`` and ``6.25 + 0.1``.
    """

    number = (1, 3, 1, 9)
    name = "Problem p09"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p09"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"0.75 (\tmp{u} - 6.25) - 0.3125 & \text{if } \tmp{u} < 6 \\ "
            r"2 (\tmp{u} - 6.25) & \text{if } 6 \le \tmp{u} \le 6.5 \\ "
            r"0.75 (\tmp{u} - 6.25) + 0.3125 & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if x < 6.0:
            return 0.75 * (x - 6.25) - 0.3125
        elif x <= 6.50:
            return 2.00 * (x - 6.25)
        else:
            return 0.75 * (x - 6.25) + 0.3125

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-5.0, 16.0, 21.0), (5.25, 11.25, 6.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=1.3, c=0.0, expected=-4.025),
        FormulaTestCase.value(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=1.3, c=0.25, expected=-7.9625),
        FormulaTestCase.value(
            params={"a": 5.25, "b": 11.25, "c_scale": 6.0}, x=7.05, c=0.0, expected=0.9124999999999999
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=6.2, c=0.0, expected=-0.09999999999999964
        ),
        FormulaTestCase.value(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=7.0, c=0.0, expected=0.875),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, expected=(-5.0, 16.0)),
        FormulaTestCase.interval_bounds(params={"a": 5.25, "b": 11.25, "c_scale": 6.0}, expected=(5.25, 11.25)),
    )
