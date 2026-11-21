"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2.1 (p. 50)`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class BurdenFairesBurden201621P50(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``2*x^3 - x^2 + x - 1``; the formula's intervals are `[-4, 4]`; `[0, 1]`.

    `f(-4)*f(4) < 0` and `f(0)*f(1) < 0`: bisection on `[0, 1]` needs 3 fewer iterations than on `[-4, 4]` for the same
    accuracy.
    """

    number = (1, 4, 7, 2)
    name = "§2.1 (p. 50)"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "c_scale",
            latex_symbol="s",
            meaning=r"The width $\param{b} - \param{a}$ of the interval, rounded to 3 significant digits.",
        ),
    )
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="§2.1 (p. 50)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"2 \tmp{u}^{3} - \tmp{u}^{2} + \tmp{u} - 1",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return 2 * x**3 - x**2 + x - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-4.0, 4.0, 8.0), (0.0, 1.0, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -4.0, "b": 4.0, "c_scale": 8.0}, x=-1.6, c=0.0, expected=-13.352000000000002
        ),
        FormulaTestCase.value(
            params={"a": -4.0, "b": 4.0, "c_scale": 8.0}, x=-1.6, c=0.25, expected=-110.87200000000001
        ),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=-0.736),
        FormulaTestCase.interval_bounds(params={"a": -4.0, "b": 4.0, "c_scale": 8.0}, expected=(-4.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
    )
