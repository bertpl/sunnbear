"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.1-3; 2.6-2(h)`` in the survey of published test problems.
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


class BurdenFairesBurden2016213(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - 7*x^2 + 14*x - 6``; the formula's intervals are `[0, 1]`; `[1,
    3.2]`; `[3.2, 4]`.

    Bisection to `1E-2` on each interval (2.1-3); all zeros to `1E-5` by Newton with deflation (2.6-2).
    """

    number = (1, 4, 7, 11)
    name = "2.1-3"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Exercises 2.1-3, 2.6-2(h)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{3} - 7 \tmp{u}^{2} + 14 \tmp{u} - 6",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**3 - 7 * x**2 + 14 * x - 6

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (1.0, 3.2, 2.2), (3.2, 4.0, 0.8)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=-2.403),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=-5.317375),
        FormulaTestCase.value(params={"a": 1.0, "b": 3.2, "c_scale": 2.2}, x=1.66, c=0.0, expected=2.525096),
        FormulaTestCase.value(params={"a": 3.2, "b": 4.0, "c_scale": 0.8}, x=3.44, c=0.0, expected=0.03238399999999993),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": 1.0, "b": 3.2, "c_scale": 2.2}, expected=(1.0, 3.2)),
        FormulaTestCase.interval_bounds(params={"a": 3.2, "b": 4.0, "c_scale": 0.8}, expected=(3.2, 4.0)),
    )
