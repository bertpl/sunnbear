"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``sin_f`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Gsl2024SinF(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``sin(x)``; the formula's intervals are ``[3, 4], [-4, -3], [-1/3, 1]``.

    The value ``-1/3`` is rounded to 12 significant digits, the most that a parameter value holds.

    Starting points 3.4, -3.3, 0.5; invalid brackets, which each bracketing solver is expected to reject: [4, 0], [1,
    1], [0.1, 0.2]; derivative given
    """

    number = (1, 3, 2, 6)
    name = "sin_f"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "c_scale",
            latex_symbol="s",
            meaning=r"The width $\param{b} - \param{a}$ of the interval, rounded to 3 significant digits.",
        ),
    )
    source = FormulaSource(
        reference=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` "
            "(copyright Reid Priedhorsky, Brian Gough), "
            "https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite "
            "no source for their functions."
        ),
        location="test_funcs.c, sin_f",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\sin{\left(\tmp{u} \right)}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.sin(x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((3.0, 4.0, 1.0), (-4.0, -3.0, 1.0), (-0.333333333333, 1.0, 1.33)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.0, expected=-0.1577456941432482),
        FormulaTestCase.value(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.25, expected=0.0914646422324372),
        FormulaTestCase.value(
            params={"a": -4.0, "b": -3.0, "c_scale": 1.0}, x=-3.7, c=0.0, expected=0.5298361409084934
        ),
        FormulaTestCase.value(
            params={"a": -0.333333333333, "b": 1.0, "c_scale": 1.33}, x=0.0666667, c=0.0, expected=0.06661732818267964
        ),
        FormulaTestCase.interval_bounds(params={"a": 3.0, "b": 4.0, "c_scale": 1.0}, expected=(3.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": -4.0, "b": -3.0, "c_scale": 1.0}, expected=(-4.0, -3.0)),
        FormulaTestCase.interval_bounds(
            params={"a": -0.333333333333, "b": 1.0, "c_scale": 1.33}, expected=(-0.333333333333, 1.0)
        ),
    )
