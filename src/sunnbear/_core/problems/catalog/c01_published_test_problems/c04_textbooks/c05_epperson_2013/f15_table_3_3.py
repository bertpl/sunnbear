"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``§3.2 (p. 100), Fig. 3.4, Table 3.3; Ex. 3.19, Table 3.16`` in the survey
of published test problems.
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


class Epperson2013Table33(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``(20*x - 1)/(19*x)``; the formula's intervals are `[0.01, 1]` (Table
    3.16); `[-0.2, 0.2]` (Fig. 3.4).

    Root 0.05. Table 3.3: the first Newton step from `x0 = 1, 0.5, 0.25, 0.125, 0.0625` gives `x1 < 0` until `x0 =
    1/16`. Table 3.16: the hybrid method (Algorithm 3.6), from `x0 = 0.01, x1 = 1`.
    """

    number = (1, 4, 5, 15)
    name = "Table 3.3"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "§3.2 (p. 100), Fig. 3.4, Table 3.3; Example 3.19, Table 3.16"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\frac{20 \tmp{u} - 1}{19 \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A hyperbola with 1 simple root, and on $[-0.2, 0.2]$ also a pole, where the function changes sign as well."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (20 * x - 1) / (19 * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.01, 1.0, 0.99), (-0.2, 0.2, 0.4)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.01, "b": 1.0, "c_scale": 0.99}, x=0.307, c=0.0, expected=0.8811932110406309
        ),
        FormulaTestCase.value(
            params={"a": 0.01, "b": 1.0, "c_scale": 0.99}, x=0.307, c=0.25, expected=0.16806722689075626
        ),
        FormulaTestCase.value(
            params={"a": -0.2, "b": 0.2, "c_scale": 0.4}, x=-0.08, c=0.0, expected=1.7105263157894737
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.01, "b": 1.0, "c_scale": 0.99}, expected=(0.01, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -0.2, "b": 0.2, "c_scale": 0.4}, expected=(-0.2, 0.2)),
    )
