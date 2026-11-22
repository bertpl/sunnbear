"""This module holds a formula of Foo, Tan (2025).

The formula comes from the row with the key ``4.2`` in the survey of published test problems.
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


class FooTan2025Section42(Formula):
    """This formula comes from Foo, Tan (2025).

    The survey writes the source's function as ``if(x = 0; 0; -x*log2(x)) - (1 - x)*log2(1 - x) - y``, with the
    parameters ``y = 0.1, 0.2, ..., 0.9``; the formula's interval is ``[0, 0.5]``.

    Definition 1 defines the entropy function on `[0, 1]`, so that `H2(0) = 0`, the limit of `-x*log2(x)` at `x = 0`.
    The row writes that value of the term at `x = 0` as a conditional, and keeps the rest of eq. (6) as printed. Eq.
    (21) prints the 9 roots with 14 decimals, from `0.01298686205551` (`y = 0.1`) to `0.31601934632361` (`y = 0.9`); the
    last decimal of the roots for `y = 0.1` to `0.4` is truncated, not rounded. Starting values solve `4*x*(1 - x) = y`
    or `(4*x*(1 - x))^(1/log(4)) = y`.
    """

    number = (1, 2, 15, 1)
    name = "Section 4.2"
    params = (FormulaParam("y", latex_symbol="y"),)
    location_in_publication = "Section 4.2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.5 \c"),),
        expression=(
            r"\begin{cases} 0 & \text{for}\: \tmp{u} = 0 \\- \tmp{u} \log_{2}{\left(\tmp{u} \right)} & "
            r"\text{otherwise} \end{cases} - \left(1 - \tmp{u}\right) \log_{2}{\left(1 - \tmp{u} "
            r"\right)} - \param{y}"
        ),
        interval="[0, 0.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, y: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.5 * c
        return ((0) if (x) == (0) else (-x * math.log2(x))) - (1 - x) * math.log2(1 - x) - y

    def interval_bounds(self, y: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("y",),
                rows=((0.1,), (0.2,), (0.3,), (0.4,), (0.5,), (0.6,), (0.7,), (0.8,), (0.9,)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"y": 0.1}, x=0.15, c=0.0, expected=0.5098403047164004),
        FormulaTestCase.value(params={"y": 0.1}, x=0.15, c=0.25, expected=0.06866093149667019),
        FormulaTestCase.value(params={"y": 0.2}, x=0.15, c=0.0, expected=0.4098403047164004),
        FormulaTestCase.value(params={"y": 0.3}, x=0.15, c=0.0, expected=0.3098403047164004),
        FormulaTestCase.value(params={"y": 0.4}, x=0.15, c=0.0, expected=0.20984030471640042),
        FormulaTestCase.value(params={"y": 0.5}, x=0.15, c=0.0, expected=0.10984030471640041),
        FormulaTestCase.value(params={"y": 0.6}, x=0.15, c=0.0, expected=0.00984030471640041),
        FormulaTestCase.value(params={"y": 0.7}, x=0.15, c=0.0, expected=-0.09015969528359959),
        FormulaTestCase.value(params={"y": 0.8}, x=0.15, c=0.0, expected=-0.19015969528359958),
        FormulaTestCase.value(params={"y": 0.9}, x=0.15, c=0.0, expected=-0.2901596952835996),
        FormulaTestCase.interval_bounds(params={"y": 0.1}, expected=(0.0, 0.5)),
    )
