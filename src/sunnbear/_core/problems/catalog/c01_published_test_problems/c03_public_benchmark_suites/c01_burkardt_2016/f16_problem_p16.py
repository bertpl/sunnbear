"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p16`` in the survey of published test problems.
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


class Burkardt2016ProblemP16(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``pi*(x - m)/180.0 - e*sin(pi*x/180.0)``, with the parameters ``e = 0.8,
    m = 5.0``; the formula's intervals are `[m - 180.0, m + 180.0]` (rang); `[0.0, m + 180.0]` (starts 1 and 2).

    The `rang` interval is `[-175.0, 185.0]`. Here `e` is the orbit's eccentricity, not Euler's number, and x and m are
    in degrees. The source's starting points, in order, are `0.0`, `m + 180.0` and `m`. The comment's table of sample
    results lists x for the row's `e = 0.8`, `m = 5` (`22.656579`) and for 13 other pairs of e and m. The function
    `p16_root` returns 22.65657866956775, but `p16_root_num` returns 0, so the drivers print "Exact root not known". The
    code writes the title as `'Kepler''s Eccentric Anomaly Equation, in degrees'`; Python reads the doubled quote as 2
    adjacent string literals, so `p16_title` returns the title without the apostrophe, and `name` gives the title as
    meant.
    """

    number = (1, 3, 1, 16)
    name = "Problem p16"
    params = (
        FormulaParam("e", latex_symbol="e"),
        FormulaParam("m", latex_symbol="m"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p16"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\frac{\pi \left(\tmp{u} - \param{m}\right)}{180.0} - \param{e} \sin{\left(\frac{\pi "
            r"\tmp{u}}{180.0} \right)}"
        ),
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, e: float, m: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.pi * (x - m) / 180.0 - e * math.sin(math.pi * x / 180.0)

    def interval_bounds(self, e: float, m: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("e", "m", "a", "b", "c_scale"),
                rows=((0.8, 5.0, -175.0, 185.0, 360.0), (0.8, 5.0, 0.0, 185.0, 185.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"e": 0.8, "m": 5.0, "a": -175.0, "b": 185.0, "c_scale": 360.0},
            x=-67.0,
            c=0.0,
            expected=-0.520233178673965,
        ),
        FormulaTestCase.value(
            params={"e": 0.8, "m": 5.0, "a": -175.0, "b": 185.0, "c_scale": 360.0},
            x=-67.0,
            c=0.25,
            expected=-2.514848485439395,
        ),
        FormulaTestCase.value(
            params={"e": 0.8, "m": 5.0, "a": 0.0, "b": 185.0, "c_scale": 185.0},
            x=55.5,
            c=0.0,
            expected=0.22209032135952392,
        ),
        FormulaTestCase.interval_bounds(
            params={"e": 0.8, "m": 5.0, "a": -175.0, "b": 185.0, "c_scale": 360.0}, expected=(-175.0, 185.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"e": 0.8, "m": 5.0, "a": 0.0, "b": 185.0, "c_scale": 185.0}, expected=(0.0, 185.0)
        ),
    )
