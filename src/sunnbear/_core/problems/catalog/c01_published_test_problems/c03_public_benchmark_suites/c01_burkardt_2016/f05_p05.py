"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p05`` in the survey of published test problems.
"""

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


class Burkardt2016P05(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``(x + 3.0)*(x - 1.0)*(x - 1.0)``; the formula's intervals are `[-1000.0,
    1000.0]` (rang); `[-5.0, 2.0]` (starts 2 and 1).

    The source's starting points, in order, are `2.0` and `-5.0`.
    """

    number = (1, 3, 1, 5)
    name = "p05"
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
        location="Problem p05",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\tmp{u} + 3.0\right) \left(\tmp{u} - 1.0\right) \left(\tmp{u} - 1.0\right)",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x + 3.0) * (x - 1.0) * (x - 1.0)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-1000.0, 1000.0, 2000.0), (-5.0, 2.0, 7.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 1000.0, "c_scale": 2000.0}, x=-400.0, c=0.0, expected=-63837997.0
        ),
        FormulaTestCase.value(
            params={"a": -1000.0, "b": 1000.0, "c_scale": 2000.0}, x=-400.0, c=0.25, expected=-728185497.0
        ),
        FormulaTestCase.value(params={"a": -5.0, "b": 2.0, "c_scale": 7.0}, x=-2.9, c=0.0, expected=1.5210000000000012),
        FormulaTestCase.interval_bounds(
            params={"a": -1000.0, "b": 1000.0, "c_scale": 2000.0}, expected=(-1000.0, 1000.0)
        ),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 2.0, "c_scale": 7.0}, expected=(-5.0, 2.0)),
    )
