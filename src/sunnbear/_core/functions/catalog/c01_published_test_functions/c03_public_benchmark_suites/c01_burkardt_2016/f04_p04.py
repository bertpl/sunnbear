"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p04`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Burkardt2016P04(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 1.0/(100.0*x*x)``; the formula's intervals are `[0.00001,
    20.0]` (rang); `[0.03, 1.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.03` and `1.0`.

    With ``modified = 1``, the formula evaluates the published function at ``x*exp(-c*ln(b/a))`` on the published
    interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c`` and never reaches 0. As ``c`` goes from
    0 to 1, the root moves by the interval's full width in log scale.

    The published test function on ``[1e-05, 20]`` does not satisfy the benchmark suite inclusion conditions, because
    the interval spans orders of magnitude next to the pole of ``1/(100*x*x)`` at 0.

    A shift along x by ``c_scale*c`` takes ``a`` to the pole at 0 for a small ``c``, so the range of ``c`` in which
    ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0`` is narrower than the minimum width that the
    conditions require.
    """

    number = (1, 3, 1, 4)
    name = "p04"
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
        location="p04",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x*exp(-c*ln(b/a))``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - c_scale * c
        else:
            x = x * math.exp(-c * math.log(b / a))
        return math.exp(x) - 1.0 / (100.0 * x * x)

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
                    (0.03, 1.0, 0.97, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((1e-05, 20.0, 20.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0, "modified": 0.0},
            x=6.00001,
            c=0.0,
            expected=403.43255002398956,
        ),
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0, "modified": 0.0},
            x=6.00001,
            c=0.25,
            expected=2.7083092114102434,
        ),
        FormulaTestCase.value(
            params={"a": 0.03, "b": 1.0, "c_scale": 0.97, "modified": 0.0}, x=0.321, c=0.0, expected=1.2814568333078415
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0, "modified": 0.0}, expected=(1e-05, 20.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.03, "b": 1.0, "c_scale": 0.97, "modified": 0.0}, expected=(0.03, 1.0)
        ),
        FormulaTestCase.value(
            params={"a": 1e-05, "b": 20.0, "c_scale": 20.0, "modified": 1.0},
            x=0.0603418,
            c=0.25,
            expected=-3882.9917266298216,
        ),
    )
