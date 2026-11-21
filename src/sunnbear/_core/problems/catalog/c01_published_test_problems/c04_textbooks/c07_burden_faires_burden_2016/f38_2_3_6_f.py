"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-6(f)`` in the survey of published test problems.
"""

import math

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


class BurdenFairesBurden2016236F(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``sin(x) - exp(-x)``; the formula's intervals are `[0, 1]`; `[3, 4]`;
    `[6, 7]`.

    As 2.3-6(a).
    """

    number = (1, 4, 7, 38)
    name = "2.3-6(f)"
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
        location="Exercise 2.3-6(f)",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\sin{\left(\tmp{u} \right)} - e^{- \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(x) - math.exp(-x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.0, 1.0), (3.0, 4.0, 1.0), (6.0, 7.0, 1.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.0, expected=-0.44529801402037833),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, x=0.3, c=0.25, expected=-0.9012502552300357),
        FormulaTestCase.value(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.0, expected=-0.19462886154448822),
        FormulaTestCase.value(params={"a": 6.0, "b": 7.0, "c_scale": 1.0}, x=6.3, c=0.0, expected=0.014977595707320806),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.0, "c_scale": 1.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, expected=(3.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": 6.0, "b": 7.0, "c_scale": 1.0}, expected=(6.0, 7.0)),
    )
