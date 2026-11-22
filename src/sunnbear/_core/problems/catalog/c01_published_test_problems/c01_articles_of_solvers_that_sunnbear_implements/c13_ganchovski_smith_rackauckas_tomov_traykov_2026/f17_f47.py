"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the rows with the keys ``f47`` and ``f48`` in the survey of published test problems.
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


class GanchovskiSmithRackauckasTomovTraykov2026F47(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``1/sqrt(x) - 2*log(5*10^k*sqrt(x)) + 0.8``:

    - f47, with ``k = 3``: ``1/sqrt(x) - 2*log(5*10^3*sqrt(x)) + 0.8``; the formula's interval is ``[0.0005, 0.5]``
    - f48, with ``k = 7``: ``1/sqrt(x) - 2*log(5*10^7*sqrt(x)) + 0.8``; the formula's interval is ``[0.0005, 0.5]``
    """

    number = (1, 1, 13, 17)
    name = "f47"
    params = (FormulaParam("k", latex_symbol="k"),)
    location_in_publication = "Table 2, f47 and f48"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.499 \c"),),
        expression=(r"\frac{1}{\sqrt{\tmp{u}}} - 2 \ln{\left(5 \cdot 10^{\param{k}} \sqrt{\tmp{u}} \right)} + " r"0.8"),
        interval="[0.0005, 0.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.499 * c
        return 1 / math.sqrt(x) - 2 * math.log(5 * 10**k * math.sqrt(x)) + 0.8

    def interval_bounds(self, k: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0005, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("k",), rows=((3.0,), (7.0,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"k": 3.0}, x=0.15035, c=0.0, expected=-11.760615174862355),
        FormulaTestCase.value(params={"k": 3.0}, x=0.15035, c=0.25, expected=-6.319223455335856),
        FormulaTestCase.value(params={"k": 7.0}, x=0.15035, c=0.0, expected=-30.181295918814723),
        FormulaTestCase.interval_bounds(params={"k": 3.0}, expected=(0.0005, 0.5)),
    )
