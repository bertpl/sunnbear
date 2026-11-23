"""This module holds a formula of SciPy (2026).

The formula comes from the row with the key ``aps15_f`` in the survey of published test problems.
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


class Scipy2026FunctionAps15F(Formula):
    """This formula comes from SciPy (2026).

    The survey writes the source's function as ``-0.859`` (x < 0); ``exp((n + 1)*x/2*1000) - 1.859`` (0 <= x <=
    2*1e-3/(1 + n)); ``e - 1.859`` (x > 2*1e-3/(1 + n)), with the parameters ``n = 20, 21, ..., 40, 100, 200, ...,
    1000``; the formula's interval is ``[-1000, 1e-4]``.

    IDs aps.15.00–aps.15.30; smoothness 0; the interval starts at -1000, where Alefeld–Potra–Shi (1995), Table I, and
    their driver start it at -10^4; ``e`` is ``np.e``; the middle piece is exponential, not linear as the docstring
    says; derivatives given
    """

    number = (1, 3, 8, 8)
    name = "Function aps15_f"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Collection “aps”, aps15_f"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1000 \c"),),
        expression=(
            r"\begin{cases} "
            r"-0.859 & \text{if } \tmp{u} < 0 \\ "
            r"\exp\left(\frac{(\param{n} + 1) \tmp{u}}{2} \cdot 1000\right) - 1.859 "
            r"& \text{if } \tmp{u} \le \frac{2 \cdot 10^{-3}}{1 + \param{n}} \\ "
            r"e - 1.859 & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[-1000, 10^{-4}]",
        summary=(
            r"A continuous function, flat outside a band within $10^{-4}$ of the upper bound, across which it rises "
            r"exponentially through 1 simple root, more steeply for larger $\param{n}$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1000.0 * c
        if x < 0.0:
            return -0.859
        elif x <= 2 * 1e-3 / (1 + n):
            return math.exp((n + 1) * x / 2 * 1000) - 1.859
        else:
            return math.e - 1.859

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1000.0, 0.0001)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=(
                    (20.0,),
                    (21.0,),
                    (22.0,),
                    (23.0,),
                    (24.0,),
                    (25.0,),
                    (26.0,),
                    (27.0,),
                    (28.0,),
                    (29.0,),
                    (30.0,),
                    (31.0,),
                    (32.0,),
                    (33.0,),
                    (34.0,),
                    (35.0,),
                    (36.0,),
                    (37.0,),
                    (38.0,),
                    (39.0,),
                    (40.0,),
                    (100.0,),
                    (200.0,),
                    (300.0,),
                    (400.0,),
                    (500.0,),
                    (600.0,),
                    (700.0,),
                    (800.0,),
                    (900.0,),
                    (1000.0,),
                ),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 20.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 20.0}, x=-700.0, c=0.25, expected=-0.859),
        FormulaTestCase.value(params={"n": 21.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 22.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 23.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 24.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 25.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 26.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 27.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 28.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 29.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 30.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 31.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 32.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 33.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 34.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 35.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 36.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 37.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 38.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 39.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 40.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 100.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 200.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 300.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 400.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 500.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 600.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 700.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 800.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 900.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 1000.0}, x=-700.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 20.0}, x=5e-05, c=0.0, expected=-0.1685411516209086),
        FormulaTestCase.value(params={"n": 20.0}, x=9.8e-05, c=0.0, expected=0.8592818284590452),
        FormulaTestCase.interval_bounds(params={"n": 20.0}, expected=(-1000.0, 0.0001)),
    )
