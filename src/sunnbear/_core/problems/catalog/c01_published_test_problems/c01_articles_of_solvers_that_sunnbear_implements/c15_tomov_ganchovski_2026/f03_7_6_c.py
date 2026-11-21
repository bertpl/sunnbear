"""This module holds a formula of Tomov, Ganchovski (2026).

The formula comes from the row with the key ``7.6-c`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class TomovGanchovski202676C(Formula):
    """This formula comes from Tomov, Ganchovski (2026).

    The survey writes the source's function as ``x``; the formula's interval is ``[-1, 1]``.

    The source's check replaces the function's value at the midpoint by NaN, and the solver must then report invalid
    input; the function itself is `x` at every point.
    """

    number = (1, 1, 15, 3)
    name = "7.6-c"
    params = ()
    source = FormulaSource(
        reference=(
            "Tomov, L., Ganchovski, N. (2026). Global convergence and reliable stopping in a "
            "safeguarded modified Anderson–Björck method. arXiv preprint 2610.14193. "
            "https://doi.org/10.48550/arxiv.2610.14193 (https://arxiv.org/abs/2610.14193). The authors'"
            " C# code and benchmark definitions are in "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding; Section 7.3 pins commit "
            "`9111cdcc6912401eb684a7b771df3a469795d5b8` (the preprint's reference [16]), and Section "
            "7.4 pins commit `51a6d1b421fa6b5422b974b61c88acb3ae1945bb` (reference [17])."
        ),
        location="Section 7.6, function c",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u}",
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        return x - 2.0 * c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.9),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
