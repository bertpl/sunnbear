"""This module holds a formula of Alefeld, Potra, Shi (1993).

The formula comes from the row with the key ``T5.1-13`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class AlefeldPotraShi1993T5113(Formula):
    """This formula comes from Alefeld, Potra, Shi (1993).

    The survey writes the source's function as ``n/20*(x/1.5 + sin(x) - 1)`` if ``x >= 0``; ``-n/20`` otherwise, with
    the parameters ``n = 1(1)40``, ``n`` from 1 to 40 in steps of 1; the formula's interval is ``[-10^4, pi/2]``.
    """

    number = (1, 2, 4, 5)
    name = "T5.1-13"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Alefeld, G., Potra, F. A., Shi, Y. (1993). On enclosing simple roots of nonlinear "
            "equations. Mathematics of Computation 61(204), 733–744. "
            "https://doi.org/10.1090/s0025-5718-1993-1192965-2."
        ),
        location="T5.1-13",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 10000.0 * c
        if x >= 0.0:
            return n / 20 * (x / 1.5 + math.sin(x) - 1)
        else:
            return -n / 20

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10000.0, 1.5707963267948966)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=(
                    (1.0,),
                    (2.0,),
                    (3.0,),
                    (4.0,),
                    (5.0,),
                    (6.0,),
                    (7.0,),
                    (8.0,),
                    (9.0,),
                    (10.0,),
                    (11.0,),
                    (12.0,),
                    (13.0,),
                    (14.0,),
                    (15.0,),
                    (16.0,),
                    (17.0,),
                    (18.0,),
                    (19.0,),
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
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 1.0}, x=-6999.53, c=0.0, expected=-0.05),
        FormulaTestCase.value(params={"n": 1.0}, x=-6999.53, c=0.25, expected=-0.05),
        FormulaTestCase.value(params={"n": 2.0}, x=-6999.53, c=0.0, expected=-0.1),
        FormulaTestCase.value(params={"n": 3.0}, x=-6999.53, c=0.0, expected=-0.15),
        FormulaTestCase.value(params={"n": 4.0}, x=-6999.53, c=0.0, expected=-0.2),
        FormulaTestCase.value(params={"n": 5.0}, x=-6999.53, c=0.0, expected=-0.25),
        FormulaTestCase.value(params={"n": 6.0}, x=-6999.53, c=0.0, expected=-0.3),
        FormulaTestCase.value(params={"n": 7.0}, x=-6999.53, c=0.0, expected=-0.35),
        FormulaTestCase.value(params={"n": 8.0}, x=-6999.53, c=0.0, expected=-0.4),
        FormulaTestCase.value(params={"n": 9.0}, x=-6999.53, c=0.0, expected=-0.45),
        FormulaTestCase.value(params={"n": 10.0}, x=-6999.53, c=0.0, expected=-0.5),
        FormulaTestCase.value(params={"n": 11.0}, x=-6999.53, c=0.0, expected=-0.55),
        FormulaTestCase.value(params={"n": 12.0}, x=-6999.53, c=0.0, expected=-0.6),
        FormulaTestCase.value(params={"n": 13.0}, x=-6999.53, c=0.0, expected=-0.65),
        FormulaTestCase.value(params={"n": 14.0}, x=-6999.53, c=0.0, expected=-0.7),
        FormulaTestCase.value(params={"n": 15.0}, x=-6999.53, c=0.0, expected=-0.75),
        FormulaTestCase.value(params={"n": 16.0}, x=-6999.53, c=0.0, expected=-0.8),
        FormulaTestCase.value(params={"n": 17.0}, x=-6999.53, c=0.0, expected=-0.85),
        FormulaTestCase.value(params={"n": 18.0}, x=-6999.53, c=0.0, expected=-0.9),
        FormulaTestCase.value(params={"n": 19.0}, x=-6999.53, c=0.0, expected=-0.95),
        FormulaTestCase.value(params={"n": 20.0}, x=-6999.53, c=0.0, expected=-1.0),
        FormulaTestCase.value(params={"n": 21.0}, x=-6999.53, c=0.0, expected=-1.05),
        FormulaTestCase.value(params={"n": 22.0}, x=-6999.53, c=0.0, expected=-1.1),
        FormulaTestCase.value(params={"n": 23.0}, x=-6999.53, c=0.0, expected=-1.15),
        FormulaTestCase.value(params={"n": 24.0}, x=-6999.53, c=0.0, expected=-1.2),
        FormulaTestCase.value(params={"n": 25.0}, x=-6999.53, c=0.0, expected=-1.25),
        FormulaTestCase.value(params={"n": 26.0}, x=-6999.53, c=0.0, expected=-1.3),
        FormulaTestCase.value(params={"n": 27.0}, x=-6999.53, c=0.0, expected=-1.35),
        FormulaTestCase.value(params={"n": 28.0}, x=-6999.53, c=0.0, expected=-1.4),
        FormulaTestCase.value(params={"n": 29.0}, x=-6999.53, c=0.0, expected=-1.45),
        FormulaTestCase.value(params={"n": 30.0}, x=-6999.53, c=0.0, expected=-1.5),
        FormulaTestCase.value(params={"n": 31.0}, x=-6999.53, c=0.0, expected=-1.55),
        FormulaTestCase.value(params={"n": 32.0}, x=-6999.53, c=0.0, expected=-1.6),
        FormulaTestCase.value(params={"n": 33.0}, x=-6999.53, c=0.0, expected=-1.65),
        FormulaTestCase.value(params={"n": 34.0}, x=-6999.53, c=0.0, expected=-1.7),
        FormulaTestCase.value(params={"n": 35.0}, x=-6999.53, c=0.0, expected=-1.75),
        FormulaTestCase.value(params={"n": 36.0}, x=-6999.53, c=0.0, expected=-1.8),
        FormulaTestCase.value(params={"n": 37.0}, x=-6999.53, c=0.0, expected=-1.85),
        FormulaTestCase.value(params={"n": 38.0}, x=-6999.53, c=0.0, expected=-1.9),
        FormulaTestCase.value(params={"n": 39.0}, x=-6999.53, c=0.0, expected=-1.95),
        FormulaTestCase.value(params={"n": 40.0}, x=-6999.53, c=0.0, expected=-2.0),
        FormulaTestCase.value(params={"n": 1.0}, x=1.0, c=0.0, expected=0.025406882573728157),
        FormulaTestCase.interval_bounds(params={"n": 1.0}, expected=(-10000.0, 1.5707963267948966)),
    )
