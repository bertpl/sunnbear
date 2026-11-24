"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2.2 Ex. 2; Fig. 2.4`` in the survey of published test problems.
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


class BurdenFairesBurden2016Example2(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = (x^2 - 1)/3``; the formula's intervals are `[-1, 1]`; `[3, 4]`.

    Unique fixed point `(3 - sqrt(13))/2` on `[-1, 1]`, where `g` meets the hypotheses of Theorem 2.3. Unique fixed
    point `(3 + sqrt(13))/2` on `[3, 4]` too, though `g(4) = 5` and `g'(4) = 8/3 > 1` break those hypotheses.
    """

    number = (1, 4, 7, 5)
    name = "Example 2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "§2.2 Example 2; Fig. 2.4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u} - \frac{\tmp{u}^{2} - 1}{3}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A concave parabola that rises through its lower root, the one on $[-1, 1]$, and falls through its upper "
            "root, the one on $[3, 4]$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x) - ((x**2 - 1) / 3)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1.0, 1.0, 2.0), (3.0, 4.0, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.0, expected=-0.12000000000000002
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.25, expected=-0.8366666666666667
        ),
        FormulaTestCase.value(
            params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.0, expected=0.0033333333333335465
        ),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, expected=(3.0, 4.0)),
    )
