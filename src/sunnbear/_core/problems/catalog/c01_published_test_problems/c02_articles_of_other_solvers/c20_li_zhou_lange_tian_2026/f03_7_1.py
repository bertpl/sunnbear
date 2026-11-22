"""This module holds a formula of Li, Zhou, Lange, Tian (2026).

The formula comes from the row with the key ``7.1`` in the survey of published test problems.
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


class LiZhouLangeTian202671(Formula):
    """This formula comes from Li, Zhou, Lange, Tian (2026).

    The survey writes the source's function as ``a3*theta^m + a2*theta^2 + a1*theta + a0``, with the parameters ``{a0,
    a1, a2, a3, m} = {1, -1, 1, -1, 3}`` and ``{1, -1, -3, 1, 3}``; the formula's interval is ``(0, a)`` with ``a = 2``;
    starting values drawn from ``U(0, 2)``.

    The formula's x is the source's ``theta``. Eq. (7.1), with ``m >= 3`` real and ``a0 > 0``. The article states the
    roots ``0.4608111`` and ``1`` "for the two cases"; with the printed coefficients, the first case has root ``1`` and
    the second ``0.4608111``. Table 2.
    """

    number = (1, 2, 20, 3)
    name = "7.1"
    params = (
        FormulaParam("a0", latex_symbol="a_0"),
        FormulaParam("a1", latex_symbol="a_1"),
        FormulaParam("a2", latex_symbol="a_2"),
        FormulaParam("a3", latex_symbol="a_3"),
        FormulaParam("m", latex_symbol="m"),
    )
    location_in_publication = "Section 7.1"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{\theta}", r"\x - 2 \c"),),
        expression=(
            r"\param{a3} \tmp{\theta}^{\param{m}} + \param{a2} \tmp{\theta}^2 + \param{a1} \tmp{\theta} + \param{a0}"
        ),
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a0: float, a1: float, a2: float, a3: float, m: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return a3 * x**m + a2 * x**2 + a1 * x + a0

    def interval_bounds(self, a0: float, a1: float, a2: float, a3: float, m: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a0", "a1", "a2", "a3", "m"),
                rows=(
                    (
                        1.0,
                        -1.0,
                        1.0,
                        -1.0,
                        3.0,
                    ),
                    (
                        1.0,
                        -1.0,
                        -3.0,
                        1.0,
                        3.0,
                    ),
                ),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a0": 1.0, "a1": -1.0, "a2": 1.0, "a3": -1.0, "m": 3.0}, x=0.6, c=0.0, expected=0.544
        ),
        FormulaTestCase.value(
            params={"a0": 1.0, "a1": -1.0, "a2": 1.0, "a3": -1.0, "m": 3.0}, x=0.6, c=0.25, expected=0.909
        ),
        FormulaTestCase.value(
            params={"a0": 1.0, "a1": -1.0, "a2": -3.0, "a3": 1.0, "m": 3.0}, x=0.6, c=0.0, expected=-0.4639999999999999
        ),
        FormulaTestCase.interval_bounds(
            params={"a0": 1.0, "a1": -1.0, "a2": 1.0, "a3": -1.0, "m": 3.0}, expected=(0.0, 2.0)
        ),
    )
