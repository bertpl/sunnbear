"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p04`` in the survey of published test problems.
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


class Burkardt2016P04(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 1.0/(100.0*x*x)``; the formula's intervals are `[0.00001,
    20.0]` (rang); `[0.03, 1.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.03` and `1.0`.
    """

    number = (1, 3, 1, 4)
    name = "p04"
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
            "John Burkardt, TEST_ZERO, Python version, file `test_zero.py`, "
            "https://people.sc.fsu.edu/~jburkardt/py_src/test_zero/test_zero.py, MIT license.\n"
            "\n"
            "The file is unversioned and has no file header; the rows come from the version with sha256"
            " `658ed0a0b520eba30e87d4a08d73b444fe4f3edf14a8a94339703eca2ef9680c`. The comment of each "
            "function gives the date on which that function was last modified, and the latest is 16 "
            "October 2020, for `p16_root`. The year is 2016 because every function that the rows "
            "transcribe (`pNN_fx`, `pNN_rang`, `pNN_start` and `pNN_title`) is dated 2 December 2016 or"
            " earlier.\n"
            "\n"
            "The file cites sources for 3 of its functions, and names a 4th origin without a reference:"
            "\n"
            '- [1] George Donovan, Arnold Miller, Timothy Moreland, "Pathological Functions for '
            "Newton's Method\", American Mathematical Monthly, January 1993, pages 53-58 (no DOI in the "
            "file), for `p15`.\n"
            "- [2] Peter Colwell, Solving Kepler's Equation Over Three Centuries, Willmann-Bell, 1993, "
            "and [3] Jean Meeus, Astronomical Algorithms, Willman-Bell, 1991, for `p16`.\n"
            "- [4] Cleve Moler, Numerical Computing with MATLAB, SIAM, 2004, ISBN 978-0-898716-60-3, "
            "for `p18`.\n"
            "- `p17`'s comment says that Wallis used the function to illustrate Newton's method, with "
            "no reference.\n"
            "\n"
            "The file's `brent` solver cites Brent's 1973 book for the algorithm, not for any function."
        ),
        location="Problem p04",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"e^{\tmp{u}} - \frac{1.0}{100.0 \tmp{u} \tmp{u}}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x) - 1.0 / (100.0 * x * x)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((1e-05, 20.0, 20.0), (0.03, 1.0, 0.97)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, x=6.00001, c=0.0, expected=403.43255002398956
        ),
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, x=6.00001, c=0.25, expected=2.7083092114102434
        ),
        FormulaTestCase.value(
            params={"a": 0.03, "b": 1.0, "c_scale": 0.97}, x=0.321, c=0.0, expected=1.2814568333078415
        ),
        FormulaTestCase.interval_bounds(params={"a": 1e-05, "b": 20.0, "c_scale": 20.0}, expected=(1e-05, 20.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.03, "b": 1.0, "c_scale": 0.97}, expected=(0.03, 1.0)),
    )
