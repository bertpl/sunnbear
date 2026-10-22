"""This module holds the formula that Alefeld, Potra, Shi (1993) labels T5.1-14.

The survey describes this function in words, not as 1 expression, so a person writes this module: a change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class AlefeldPotraShi1993T5114(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``e - 1.859`` if ``x > 2*10^(-3)/(1 + n)``; ``exp((n + 1)*x/2*10^3) -
    1.859`` if ``x`` in ``[0, 2*10^(-3)/(1 + n)]``; ``-0.859`` if ``x < 0``, with the parameters ``n = 20(1)40,
    100(100)1000``, ``n`` from 20 to 40 in steps of 1 and from 100 to 1000 in steps of 100; the formula's interval is
    ``[-10^4, 10^(-4)]``.

    The print puts all of ``(n + 1)*x/2*10^3`` in the exponent, which makes the function continuous at ``x =
    2*10^(-3)/(1 + n)``.
    """

    number = (1, 2, 4, 6)
    name = "T5.1-14"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Alefeld, G., Potra, F. A., Shi, Y. (1993). On enclosing simple roots of nonlinear "
            "equations. Mathematics of Computation 61(204), 733–744. "
            "https://doi.org/10.1090/s0025-5718-1993-1192965-2."
        ),
        location="T5.1-14",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 10000.0001 * c
        if x > 2 * 10**-3 / (1 + n):
            return math.e - 1.859
        elif x >= 0.0:
            return math.exp((n + 1) * x / 2 * 10**3) - 1.859
        else:
            return -0.859

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10000.0, 0.0001)

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
            ),
        )

    cases = (
        FormulaTestCase.value(params={"n": 20.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 20.0}, x=-7000.0, c=0.25, expected=-0.859),
        FormulaTestCase.value(params={"n": 21.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 22.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 23.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 24.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 25.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 26.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 27.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 28.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 29.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 30.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 31.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 32.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 33.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 34.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 35.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 36.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 37.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 38.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 39.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 40.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 100.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 200.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 300.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 400.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 500.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 600.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 700.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 800.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 900.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 1000.0}, x=-7000.0, c=0.0, expected=-0.859),
        FormulaTestCase.value(params={"n": 20.0}, x=9.8e-05, c=0.0, expected=0.8592818284590452),
        FormulaTestCase.value(params={"n": 20.0}, x=5e-05, c=0.0, expected=-0.1685411516209086),
        FormulaTestCase.interval_bounds(params={"n": 20.0}, expected=(-10000.0, 0.0001)),
    )
