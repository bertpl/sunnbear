"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``7`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Chandrupatla1997Function7(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``0`` if ``abs(x) < 3.8*10^-4``, ``x*exp(-x^-2)`` otherwise; the
    formula's intervals are ``[-1, 4]``; ``[-2, 5]``; ``[-1, 10]``; ``[-5, 50]``; ``[-10, 100]``.

    Printed zero: ``x = 0``. The article says Brent discusses it.
    """

    number = (1, 1, 7, 7)
    name = "Function 7"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 1, function 7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } |\tmp{u}| < 3.8 \cdot 10^{-4} \\ "
            r"\tmp{u} e^{-\tmp{u}^{-2}} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "An odd function with all derivatives 0 at its root, so flat there that it is exactly 0 in floating point "
            "on a band 0.073 wide."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if abs(x) < 3.8e-4:
            return 0.0
        else:
            return x * math.exp(-(x**-2))

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (-1.0, 4.0, 5.0),
                    (-2.0, 5.0, 7.0),
                    (-1.0, 10.0, 11.0),
                    (-5.0, 50.0, 55.0),
                    (-10.0, 100.0, 110.0),
                ),
                summary="The published intervals.",
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.5, c=0.25, expected=-0.12675998655454956
        ),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, x=0.0001, c=0.0, expected=0.0),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 5.0, "c_scale": 7.0}, x=0.1, c=0.0, expected=3.7200759760208773e-45, atol=0.0
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 10.0, "c_scale": 11.0}, x=2.3, c=0.0, expected=1.9038405842623145
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 50.0, "c_scale": 55.0}, x=11.5, c=0.0, expected=11.413371409313232
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 100.0, "c_scale": 110.0}, x=23.0, c=0.0, expected=22.956562808012574
        ),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0, "c_scale": 5.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 5.0, "c_scale": 7.0}, expected=(-2.0, 5.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 10.0, "c_scale": 11.0}, expected=(-1.0, 10.0)),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 50.0, "c_scale": 55.0}, expected=(-5.0, 50.0)),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 100.0, "c_scale": 110.0}, expected=(-10.0, 100.0)),
    )
