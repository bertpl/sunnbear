"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§4.7; Ex. 4.1, 4.2`` in the survey of published test problems.
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


class Moler2004Section47(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``x^3 - 2*x - 5``; the formula's intervals are `[0, 3]` (Ex. 4.1); `[2,
    3]` (Ex. 4.2).

    §4.7 writes it as the anonymous function `G = @(z) z^3-2*z-5`, an example of syntax. Ex. 4.2: Wallis used it when he
    first presented Newton's method to the French Academy; it has 1 real root, between 2 and 3, and a pair of complex
    conjugate roots. Ex. 4.2 asks for the 3 roots symbolically and with `roots`, for the real root with `fzerotx`, and
    for a complex root by Newton's method from a complex starting value.
    """

    number = (1, 4, 3, 7)
    name = "Section 4.7"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "§4.7; Exercises 4.1, 4.2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{3} - 2 \tmp{u} - 5",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**3 - 2 * x - 5

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((0.0, 3.0, 3.0), (2.0, 3.0, 1.0)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 3.0, "c_scale": 3.0}, x=0.9, c=0.0, expected=-6.071),
        FormulaTestCase.value(params={"a": 0.0, "b": 3.0, "c_scale": 3.0}, x=0.9, c=0.25, expected=-5.296625),
        FormulaTestCase.value(params={"a": 2.0, "b": 3.0, "c_scale": 1.0}, x=2.3, c=0.0, expected=2.5669999999999975),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 3.0, "c_scale": 3.0}, expected=(0.0, 3.0)),
        FormulaTestCase.interval_bounds(params={"a": 2.0, "b": 3.0, "c_scale": 1.0}, expected=(2.0, 3.0)),
    )
