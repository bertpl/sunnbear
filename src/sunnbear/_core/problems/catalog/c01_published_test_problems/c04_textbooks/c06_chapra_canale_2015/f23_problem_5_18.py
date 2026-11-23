"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.18`` in the survey of published test problems.
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


class ChapraCanale2015Problem518(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``log(osf) = -139.34411 + 1.575701E5/Ta - 6.642308E7/Ta^2 +
    1.243800E10/Ta^3 - 8.621949E11/Ta^4``, with the parameters `Ta = T + 273.15`; `osf = 8, 10, 12` mg/L; the survey's
    interval, in the source's variable, is `[273.15, 313.15]` (`T` from 0 to 40 °C, as values of `Ta`).

    Unknown ``T``, the temperature (°C) of freshwater at 1 atm whose saturation concentration of dissolved oxygen is
    ``osf``. Bisection to an absolute error of 0.05 °C; the problem first asks how many iterations that takes. The book
    prints ``ln``.

    The formula's variable is the temperature ``T`` in °C, as ``f(T + 273.15)`` on ``[0, 40]``: the problem gives the
    formula in the absolute temperature ``Ta`` and asks for ``T``. The formula is the difference form ``log(osf) -
    (...)`` of the printed equation.
    """

    number = (1, 4, 6, 23)
    name = "Problem 5.18"
    params = (
        FormulaParam(
            "osf",
            latex_symbol="o_{sf}",
            meaning=(
                r"The saturation concentration of dissolved oxygen, in mg/L; the larger $\param{osf}$, the closer the "
                "root lies to the lower bound."
            ),
        ),
    )
    location_in_publication = "Prob. 5.18"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{T}", r"\x - 40 \c"),
            (r"\tmp{T_a}", r"\tmp{T} + 273.15"),
        ),
        expression=(
            r"\ln(\param{osf}) - \left(-139.34411 + \frac{1.575701 \cdot 10^{5}}{\tmp{T_a}} "
            r"- \frac{6.642308 \cdot 10^{7}}{\tmp{T_a}^2} + \frac{1.243800 \cdot 10^{10}}{\tmp{T_a}^3} "
            r"- \frac{8.621949 \cdot 10^{11}}{\tmp{T_a}^4}\right)"
        ),
        interval="[0, 40]",
        summary=(
            r"An increasing function of the temperature, with 1 simple root: the temperature at which freshwater's "
            r"saturation concentration of dissolved oxygen is $\param{osf}$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, osf: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 40.0 * c
        # the formula's variable is the temperature T in °C; the source's function is in Ta = T + 273.15
        t_a = x + 273.15
        return math.log(osf) - (
            -139.34411 + 1.575701e5 / t_a - 6.642308e7 / t_a**2 + 1.2438e10 / t_a**3 - 8.621949e11 / t_a**4
        )

    def interval_bounds(self, osf: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 40.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("osf",), rows=((8.0,), (10.0,), (12.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"osf": 8.0}, x=28.0, c=0.0, expected=0.021762506592685964),
        FormulaTestCase.value(params={"osf": 8.0}, x=12.0, c=0.25, expected=-0.5474113296149795),
        FormulaTestCase.value(params={"osf": 10.0}, x=28.0, c=0.0, expected=0.2449060579068957),
        FormulaTestCase.value(params={"osf": 12.0}, x=28.0, c=0.0, expected=0.42722761470085036),
        FormulaTestCase.interval_bounds(params={"osf": 8.0}, expected=(0.0, 40.0)),
    )
