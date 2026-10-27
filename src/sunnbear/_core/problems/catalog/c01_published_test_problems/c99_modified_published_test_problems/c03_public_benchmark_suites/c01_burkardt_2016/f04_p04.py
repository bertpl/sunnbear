"""This module holds formula f1.99.3.1.4, the modified version of the published formula f1.3.1.4.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.1.4 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBurkardt2016P04(Formula):
    """This formula is the modified version of formula f1.3.1.4, from Burkardt (2016).

    The survey writes the source's function as ``exp(x) - 1.0/(100.0*x*x)``; the published intervals are `[0.00001,
    20.0]` (rang); `[0.03, 1.0]` (starts 1 and 2).

    The source's starting points, in order, are `0.03` and `1.0`.

    The formula holds only the test problem on ``[1e-05, 20]``. It evaluates the published function at
    ``x*exp(-c*ln(b/a))`` on that interval, ``[a, b]``: ``c`` scales x, so that the root moves by the factor
    ``(b/a)**c`` and never reaches 0.

    As ``c`` goes from 0 to 1, the root moves by the interval's full width in log scale.

    The published test problem on ``[1e-05, 20]`` does not satisfy the benchmark suite inclusion conditions, because
    the interval spans orders of magnitude next to the pole of ``1/(100*x*x)`` at 0.

    A shift along x by ``c_scale*c`` takes ``a`` to the pole at 0 for a small ``c``, so the range of ``c`` in which
    ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0`` is narrower than the minimum width that the
    conditions require.
    """

    number = (1, 99, 3, 1, 4)
    name = "p04"
    param_names = ()
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
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x*exp(-c*ln(b/a))``, with ``[a, b] = [1e-05, 20]``."""
        x = x * math.exp(-c * math.log(20.0 / 1e-05))
        return math.exp(x) - 1.0 / (100.0 * x * x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1e-05, 20.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (FormulaTestCase.value(params={}, x=0.0603418, c=0.25, expected=-3882.9917266298216),)
