"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``f2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Scipy2026F2(Formula):
    """This formula comes from SciPy (2026).

    The survey writes the source's function as ``x^2 - 1``; the formula's interval is ``[0.5, sqrt(3)]``.

    ID original.02.00; derivatives given
    """

    number = (1, 3, 8, 2)
    name = "f2"
    params = ()
    source = FormulaSource(
        reference=(
            "SciPy 1.18.1, module `scipy/optimize/_tstutils.py`, "
            "https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/_tstutils.py. The module cites "
            "2 sources:\n"
            '- [1] Alefeld, G. E., Potra, F. A. and Shi, Y., "Algorithm 748: Enclosing Zeros of '
            'Continuous Functions", ACM Trans. Math. Softw. 21(3), September 1995, pp. 327–344, '
            'https://dl.acm.org/doi/10.1145/210089.210111; the module misprints the volume as "Volume '
            '221" and gives no issue or pages\n'
            '- [2] Chandrupatla, T. R., "A new hybrid quadratic/bisection algorithm for finding the '
            'zero of a nonlinear function without using derivatives", Advances in Engineering Software '
            "28.3 (1997): 145-149 (no DOI in the module)"
        ),
        location="Collection “original”, f2",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.23 \c"),),
        expression=r"\tmp{u}^{2} - 1",
        interval=r"[0.5, \sqrt{3}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.23 * c
        return x**2 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.7320508075688772)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.869615, c=0.0, expected=-0.24376975177499996),
        FormulaTestCase.value(params={}, x=0.869615, c=0.25, expected=-0.684026726775),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.7320508075688772)),
    )
