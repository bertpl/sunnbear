"""This module holds a formula of Tomov, Ganchovski (2026).

The formula comes from the row with the key ``(25)`` in the survey of published test problems.
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


class TomovGanchovski202625(Formula):
    """This formula comes from Tomov, Ganchovski (2026).

    The survey writes the source's function as ``x`` if ``x <= 0``; ``x + x^2`` if ``x > 0``; the formula's intervals
    are ``[-1, 1]``; ``[-3, 1]``.

    Proposition 3.5 starts an AB phase on ``[-1, 1]``. The text after it starts the hybrid method on ``[-3, 1]``, whose
    first bisection leads to the same phase.
    """

    number = (1, 1, 15, 1)
    name = "(25)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section 3, Eq. (25)"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"\tmp{u} & \text{if } \tmp{u} \le 0 \\ "
            r"\tmp{u} + \tmp{u}^2 & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if x <= 0.0:
            return x
        else:
            return x + x**2

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1.0, 1.0, 2.0), (-3.0, 1.0, 4.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.25, expected=-0.9),
        FormulaTestCase.value(params={"a": -3.0, "b": 1.0, "c_scale": 4.0}, x=-1.8, c=0.0, expected=-1.8),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": 1.0, "c_scale": 4.0}, expected=(-3.0, 1.0)),
    )
