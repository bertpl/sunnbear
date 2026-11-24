"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``§8.2, (8.14)`` in the survey of published test problems.
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


class ChapraCanale2015Equation814(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``K1/(10^6*H)*KH*pCO2 + 2*K2*K1/(10^6*H^2)*KH*pCO2 + Kw/H - H``, with the
    parameters `KH = 10^-1.46`, `K1 = 10^-6.3`, `K2 = 10^-10.3`, `Kw = 10^-14`; `pCO2 = 315, 375` ppm (1958, 2003); the
    survey's interval, in the source's variable, is `[1E-12, 1E-2]` (the pH from 2 to 12).

    Unknown ``H``, the hydrogen-ion concentration ``[H+]``, which gives the pH ``-log10(H)`` of rainwater; the book
    derives (8.14) from 5 equilibrium equations, and calls it a cubic in ``[H+]``. Bisection on the pH, from the initial
    guesses 2 and 12, which the interval gives as values of ``H``: 11 iterations, for an absolute error of 0.005, give
    5.6279 for 1958, and 35 give 5.6304; 2003 gives 5.59.

    The formula's variable is the pH, as ``f(10^-pH)`` on ``[2, 12]``: the book prints the charge balance (8.14) in
    ``H`` and bisects on the pH from 2 to 12. The constants ``KH``, ``K1``, ``K2`` and ``Kw`` are fixed; ``pCO2`` is the
    formula's parameter.
    """

    number = (1, 4, 6, 6)
    name = "Equation (8.14)"
    params = (
        FormulaParam(
            "pCO2",
            latex_symbol=r"p_{\mathrm{CO_2}}",
            meaning="The partial pressure of carbon dioxide in the air, in ppm.",
        ),
    )
    location_in_publication = "§8.2, Eq. (8.14)"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - 10 \c"),
            (r"\tmp{H}", r"10^{-\tmp{u}}"),
            (r"\tmp{K_H}", r"10^{-1.46}"),
            (r"\tmp{K_1}", r"10^{-6.3}"),
            (r"\tmp{K_2}", r"10^{-10.3}"),
            (r"\tmp{K_w}", r"10^{-14}"),
        ),
        expression=(
            r"\frac{\tmp{K_1}}{10^6 \tmp{H}} \tmp{K_H} \param{pCO2} "
            r"+ \frac{2 \tmp{K_2} \tmp{K_1}}{10^6 \tmp{H}^2} \tmp{K_H} \param{pCO2} "
            r"+ \frac{\tmp{K_w}}{\tmp{H}} - \tmp{H}"
        ),
        interval="[2, 12]",
        summary=(
            r"The charge balance of rainwater in terms of the pH, with 1 simple root and values below $10^{-4}$ in "
            r"magnitude for $4 \le \x \le 7$ but above 500 at $\x = 12$."
        ),
        notes=(r"$\tmp{u}$ is the pH of the rainwater.",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, pCO2: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10.0 * c
        # the formula's variable is the pH; the source's function is in H = 10^-pH
        h = 10.0**-x
        k_h, k_1, k_2, k_w = 10.0**-1.46, 10.0**-6.3, 10.0**-10.3, 10.0**-14
        return k_1 / (1e6 * h) * k_h * pCO2 + 2 * k_2 * k_1 / (1e6 * h**2) * k_h * pCO2 + k_w / h - h

    def interval_bounds(self, pCO2: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 12.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("pCO2",), rows=((315.0,), (375.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"pCO2": 315.0}, x=5.0, c=0.0, expected=-9.45158725187333e-06),
        FormulaTestCase.value(params={"pCO2": 315.0}, x=5.0, c=0.25, expected=-0.003162275925952294),
        FormulaTestCase.value(params={"pCO2": 375.0}, x=5.0, c=0.0, expected=-9.34731815699206e-06),
        FormulaTestCase.interval_bounds(params={"pCO2": 315.0}, expected=(2.0, 12.0)),
    )
