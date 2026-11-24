"""This module holds a formula of Norton (1985).

The formula comes from the row with the key ``9`` in the survey of published test problems.
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


class Norton1985Function9(Formula):
    """This formula comes from Norton (1985).

    The survey writes the source's function as ``x^n + a*x + b``, with the parameters `a = 0, b = 10^-4`; `n = 3, 5, 9,
    19`; the formula's interval is ``[-0.7, 1]``.

    The formula's parameters ``a_`` and ``b_`` are the source's ``a`` and ``b``, renamed because ``[a, b]`` names the
    formula's interval.

    Group II.
    """

    number = (1, 2, 2, 5)
    name = "Function 9"
    params = (
        FormulaParam("a_", latex_symbol="a"),
        FormulaParam("b_", latex_symbol="b"),
        FormulaParam("n", latex_symbol="n"),
    )
    location_in_publication = "Section 4, function 9"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.7 \c"),),
        expression=r"\tmp{u}^{\param{n}} + \param{a_} \tmp{u} + \param{b_}",
        interval="[-0.7, 1]",
        summary=(
            r"A function with 1 simple root, below $2 \cdot 10^{-4}$ in magnitude from just below that root to 1.23 "
            r"above it at $\param{n} = 19$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, b_: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.7 * c
        return x**n + a_ * x + b_

    def interval_bounds(self, a_: float, b_: float, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.7, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a_", "b_", "n"),
                rows=((0.0, 0.0001, 3.0), (0.0, 0.0001, 5.0), (0.0, 0.0001, 9.0), (0.0, 0.0001, 19.0)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a_": 0.0, "b_": 0.0001, "n": 3.0}, x=-0.19, c=0.0, expected=-0.006759),
        FormulaTestCase.value(params={"a_": 0.0, "b_": 0.0001, "n": 3.0}, x=-0.19, c=0.25, expected=-0.232508375),
        FormulaTestCase.value(
            params={"a_": 0.0, "b_": 0.0001, "n": 5.0}, x=-0.19, c=0.0, expected=-0.00014760990000000002
        ),
        FormulaTestCase.value(params={"a_": 0.0, "b_": 0.0001, "n": 9.0}, x=-0.19, c=0.0, expected=9.9677312302221e-05),
        FormulaTestCase.value(
            params={"a_": 0.0, "b_": 0.0001, "n": 19.0}, x=0.49, c=0.0, expected=0.00010129934811447123
        ),
        FormulaTestCase.interval_bounds(params={"a_": 0.0, "b_": 0.0001, "n": 3.0}, expected=(-0.7, 1.0)),
    )
