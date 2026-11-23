"""This module holds a formula of Ford (1997).

The formula comes from the row with the key ``2`` in the survey of published test problems.
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


class Ford1997Function2(Formula):
    """This formula comes from Ford (1997).

    The survey writes the source's function as ``10^-8*(x - 1)*prod(x^2 + x + i, i = 1..10)``; the formula's intervals
    are `[0.9, 1.1]`; `[0.5, 1.5]`; `[-5, 10]`.

    Printed root: `x* = 1.0`. The article says Hopgood and McKee study this function.
    """

    number = (1, 1, 8, 2)
    name = "Function 2"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Section “Numerical Tests”, function 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\frac{\left(\tmp{u} - 1\right) \prod_{i=1}^{10} \left(\tmp{u}^{2} + \tmp{u} + " r"i\right)}{10^{8}}"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"A polynomial of degree 21 with 1 real root, within 0.19 of 0 from $\x = -1$ up to that root, and growing "
            r"steeply above it."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (
            10**-8
            * (x - 1)
            * (
                (x**2 + x + (1))
                * (x**2 + x + (2))
                * (x**2 + x + (3))
                * (x**2 + x + (4))
                * (x**2 + x + (5))
                * (x**2 + x + (6))
                * (x**2 + x + (7))
                * (x**2 + x + (8))
                * (x**2 + x + (9))
                * (x**2 + x + (10))
            )
        )

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.9, 1.1, 0.2), (0.5, 1.5, 1.0), (-5.0, 10.0, 15.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.9, "b": 1.1, "c_scale": 0.2}, x=0.96, c=0.0, expected=-0.07905914659719734
        ),
        FormulaTestCase.value(
            params={"a": 0.9, "b": 1.1, "c_scale": 0.2}, x=0.96, c=0.25, expected=-0.1400565243092936
        ),
        FormulaTestCase.value(params={"a": 0.5, "b": 1.5, "c_scale": 1.0}, x=0.8, c=0.0, expected=-0.18486721613136733),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 10.0, "c_scale": 15.0}, x=-0.5, c=0.0, expected=-0.024747659447550772
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.9, "b": 1.1, "c_scale": 0.2}, expected=(0.9, 1.1)),
        FormulaTestCase.interval_bounds(params={"a": 0.5, "b": 1.5, "c_scale": 1.0}, expected=(0.5, 1.5)),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 10.0, "c_scale": 15.0}, expected=(-5.0, 10.0)),
    )
