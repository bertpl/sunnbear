"""This module holds formula f1.99.3.1.12, the modified version of the published formula f1.3.1.12.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.1.12 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable
from sunnbear._core.utils.floats import TINY_LINEAR_TERM_SLOPE


class ModifiedBurkardt2016P12(Formula):
    """This formula is the modified version of formula f1.3.1.12, from Burkardt (2016).

    The survey writes the source's function as ``-exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x < 1.0);
    ``0.0`` (x = 1.0); ``+exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x > 1.0), with the parameters
    ``factor = 1000.0``; the published intervals are ``[-4.0, 4.1]`` (rang); ``[0.50, 2.0]`` (starts 2 and 1).

    The source's starting points, in order, are ``2.0``, ``0.50`` and ``4.0``.

    The formula adds ``TINY_LINEAR_TERM_SLOPE*(x - 1)`` to the published function, on the published intervals; ``c``
    shifts x by the rule of category 1, before the formula adds the term. `TINY_LINEAR_TERM_SLOPE` is about 4.5e-277.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    In float64, the published function is exactly 0 within about 0.04 of the root, because its true values there lie
    below float64's range; no way of writing the function avoids these exact zeros.

    With the term, f is exactly 0 only within about 5e-48 of the root, where the term underflows too; beyond about 0.04
    from the root, the term changes f by less than the rounding error of f.

    The modification changes what the test problem tests: with the published function, a solver may stop at any
    x-value within about 0.04 of the root, while with the term a solver must locate the root, near which f is the
    linear term.
    """

    number = (1, 99, 3, 1, 12)
    name = "p12"
    param_names = ("factor", "a", "b", "c_scale")
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
        location="p12",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, factor: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, and add ``TINY_LINEAR_TERM_SLOPE*(y - 1)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if x < 1.0:
            published_value = -math.exp(math.log(factor) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)
        elif x == 1.0:
            published_value = 0.0
        else:
            published_value = math.exp(math.log(factor) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)
        return published_value + TINY_LINEAR_TERM_SLOPE * (x - 1.0)

    def interval_bounds(self, factor: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("factor", "a", "b", "c_scale"),
                rows=(
                    (1000.0, -4.0, 4.1, 8.1),
                    (1000.0, 0.5, 2.0, 1.5),
                ),
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, expected=(-4.0, 4.1)
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=-1.57, c=0.25, expected=-4382.445368656935
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1},
            x=1.0001,
            c=0.0,
            expected=4.512985939661577e-281,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"factor": 1000.0, "a": 0.5, "b": 2.0, "c_scale": 1.5}, expected=(0.5, 2.0)
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": 0.5, "b": 2.0, "c_scale": 1.5},
            x=1.0001,
            c=0.0,
            expected=4.512985939661577e-281,
            atol=0.0,
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=1.0, c=0.0, expected=0.0, atol=0.0
        ),
    )
