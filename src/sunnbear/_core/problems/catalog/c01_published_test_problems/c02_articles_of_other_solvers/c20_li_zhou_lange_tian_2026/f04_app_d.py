"""This module holds a formula of Li, Zhou, Lange, Tian (2026).

The formula comes from the row with the key ``App. D`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class LiZhouLangeTian2026AppD(Formula):
    """This formula comes from Li, Zhou, Lange, Tian (2026).

    The survey writes the source's function as ``x^3 - 3*x^2 + x + 1``; the formula's interval is `(0, 2)`; starting
    value `x0 = 0`.

    Example of the R code for eq. (7.1) (`a3 = 1`, `a2 = -3`, `a1 = 1`, `a0 = 1`, `m = 3`); output root `1`. Appendix E
    solves the same cubic in closed form: roots `2.4142136`, `-0.4142136`, `1`.
    """

    number = (1, 2, 20, 4)
    name = "App. D"
    params = ()
    source = FormulaSource(
        reference=(
            "Li, X.-J., Zhou, H., Lange, K., Tian, G.-L. (2026). The upper–crossing/solution (US) "
            "algorithm with strongly stable convergence and an acceleration technique for root–finding "
            "problems. Statistics and Computing 36(4), 197. https://doi.org/10.1007/s11222-026-10902-z."
            " Preprint: arXiv 2212.00797v2 (8 November 2025), https://arxiv.org/abs/2212.00797v2. The "
            "authors' R code: https://github.com/Xunjian-Li/US-algorithm.git."
        ),
        location="Appendix D",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u}^{3} - 3 \tmp{u}^{2} + \tmp{u} + 1",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x**3 - 3 * x**2 + x + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=0.736),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=1.071),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
