"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.18`` in the survey of published test problems. The survey gives
this function as 1 expression with a change of its variable to the temperature `T` in °C, as `f(T + 273.15)`, which the
module generator, `scripts/literature_test_problems/formula_modules.py`, cannot apply, so a person writes this module: a
change of the formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ChapraCanale2015Prob518(Formula):
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

    number = (1, 4, 6, 24)
    name = "Prob. 5.18"
    param_names = ("osf",)
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 5.18",
    )

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
        return (ParamTable(names=("osf",), rows=((8.0,), (10.0,), (12.0,))),)

    cases = (
        FormulaTestCase.value(params={"osf": 8.0}, x=28.0, c=0.0, expected=0.021762506592685964),
        FormulaTestCase.value(params={"osf": 8.0}, x=12.0, c=0.25, expected=-0.5474113296149795),
        FormulaTestCase.value(params={"osf": 10.0}, x=28.0, c=0.0, expected=0.2449060579068957),
        FormulaTestCase.value(params={"osf": 12.0}, x=28.0, c=0.0, expected=0.42722761470085036),
        FormulaTestCase.interval_bounds(params={"osf": 8.0}, expected=(0.0, 40.0)),
    )
