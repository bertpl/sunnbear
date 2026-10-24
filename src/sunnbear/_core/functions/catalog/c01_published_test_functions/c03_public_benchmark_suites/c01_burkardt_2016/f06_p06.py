"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p06`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Burkardt2016P06(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 2.0 - 1.0/(10.0*x)^2 + 2.0/(100.0*x)^3``; the formula's
    intervals are `[0.00001, 20.0]` (rang); `[0.0002, 2.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.0002` and `2.0`. The title has `- 2 / ( 100 * X )^3` where the code
    and the docstring have `+`. The function does not change sign on `rang`, `[0.00001, 20.0]`, which holds 2 roots,
    about `0.0001999992` and `0.7032048404`; `p06_root` returns only the 2nd, `0.7032048403631358`.

    With ``modified = 1``, the interval ``[1e-05, 20]`` becomes ``[0.08, 20]``: its lower bound moves right of the first
    root, near 0.00019, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with
    ``c_scale`` the rounded width of the new interval.

    The published test function on ``[1e-05, 20]`` fails a benchmark suite's checks of its test functions, because the
    published interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 3, 1, 6)
    name = "p06"
    param_names = ("a", "b", "c_scale", "modified")
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
        location="p06",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return math.exp(x) - 2.0 - 1.0 / (10.0 * x) ** 2 + 2.0 / (100.0 * x) ** 3

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (1e-05, 20.0, 20.0, 0.0),
                    (0.0002, 2.0, 2.0, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.08, 20.0, 19.9, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0, "modified": 0.0},
            x=6.00001,
            c=0.0,
            expected=401.4325500332488,
        ),
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0, "modified": 0.0},
            x=6.00001,
            c=0.25,
            expected=0.7083112113502446,
        ),
        FormulaTestCase.value(
            params={"a": 0.0002, "b": 2.0, "c_scale": 2.0, "modified": 0.0},
            x=0.60014,
            c=0.0,
            expected=-0.2053816516894782,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0, "modified": 0.0}, expected=(1e-05, 20.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0002, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, expected=(0.0002, 2.0)
        ),
        FormulaTestCase.value(
            params={"a": 0.08, "b": 20.0, "c_scale": 19.9, "modified": 1.0},
            x=6.056,
            c=0.25,
            expected=0.9390697531278249,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.08, "b": 20.0, "c_scale": 19.9, "modified": 1.0}, expected=(0.08, 20.0)
        ),
    )
