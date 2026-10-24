"""This module holds a formula of Tomov, Ganchovski (2026).

The formula comes from the row with the key ``(25)`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class TomovGanchovski202625(Formula):
    """This formula comes from Tomov, Ganchovski (2026).

    The survey writes the source's function as ``x`` if ``x <= 0``; ``x + x^2`` if ``x > 0``; the formula's intervals
    are ``[-1, 1]``; ``[-3, 1]``.

    Proposition 3.5 starts an AB phase on ``[-1, 1]``. The text after it starts the hybrid method on ``[-3, 1]``, whose
    first bisection leads to the same phase.
    """

    number = (1, 1, 15, 1)
    name = "(25)"
    param_names = ("a", "b", "c_scale")
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
        location="(25)",
    )

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
        return (ParamTable(names=("a", "b", "c_scale"), rows=((-1.0, 1.0, 2.0), (-3.0, 1.0, 4.0))),)

    test_cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.25, expected=-0.9),
        FormulaTestCase.value(params={"a": -3.0, "b": 1.0, "c_scale": 4.0}, x=-1.8, c=0.0, expected=-1.8),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": 1.0, "c_scale": 4.0}, expected=(-3.0, 1.0)),
    )
