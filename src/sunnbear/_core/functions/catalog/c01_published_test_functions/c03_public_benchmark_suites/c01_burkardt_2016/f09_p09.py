"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p09`` in the survey of published test problems. The survey gives this
function as a description, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Burkardt2016P09(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``0.75*(x - 6.25) - 0.3125`` (x < 6.0); ``2.00*(x - 6.25)`` (6.0 <= x <=
    6.50); ``0.75*(x - 6.25) + 0.3125`` (x > 6.50); the formula's intervals are ``[-5.0, 16.0]`` (rang); ``[6.25 - 1.0,
    6.25 + 5.0]`` (starts 2 and 1).

    The source's starting points, in order, are ``6.25 + 5.0``, ``6.25 - 1.0`` and ``6.25 + 0.1``.
    """

    number = (1, 3, 1, 9)
    name = "p09"
    param_names = ("a", "b", "c_scale")
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
        location="p09",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if x < 6.0:
            return 0.75 * (x - 6.25) - 0.3125
        elif x <= 6.50:
            return 2.00 * (x - 6.25)
        else:
            return 0.75 * (x - 6.25) + 0.3125

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((-5.0, 16.0, 21.0), (5.25, 11.25, 6.0))),)

    test_cases = (
        FormulaTestCase.value(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=1.3, c=0.0, expected=-4.025),
        FormulaTestCase.value(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=1.3, c=0.25, expected=-7.9625),
        FormulaTestCase.value(
            params={"a": 5.25, "b": 11.25, "c_scale": 6.0}, x=7.05, c=0.0, expected=0.9124999999999999
        ),
        FormulaTestCase.value(
            params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=6.2, c=0.0, expected=-0.09999999999999964
        ),
        FormulaTestCase.value(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, x=7.0, c=0.0, expected=0.875),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 16.0, "c_scale": 21.0}, expected=(-5.0, 16.0)),
        FormulaTestCase.interval_bounds(params={"a": 5.25, "b": 11.25, "c_scale": 6.0}, expected=(5.25, 11.25)),
    )
