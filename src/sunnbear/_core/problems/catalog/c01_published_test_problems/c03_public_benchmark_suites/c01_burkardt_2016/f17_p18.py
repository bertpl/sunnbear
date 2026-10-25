"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p18`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Burkardt2016P18(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``10.0^14*(1.0*x^7 - 7.0*x^6 + 21.0*x^5 - 35.0*x^4 + 35.0*x^3 - 21.0*x^2
    + 7.0*x - 1.0)``; the formula's intervals are `[0.988, 1.012]` (rang); `[0.990, 1.013]` (starts 1 and 2).

    The source's starting points, in order, are `0.990` and `1.013`. The code also holds the Horner form of the
    polynomial, switched off by `horners = False`.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``10.0**14*(x - 1)**7``,
    on the published intervals, and ``c`` shifts x as category 1 states.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the terms of the
    published form cancel:

    - on ``[0.988, 1.012]``, f is exactly 0 at many x-values, up to about 0.01 from the root, and the conditions require
      bisection to spend a fixed number of evaluations, while bisection stops early where a midpoint lands on an exact 0
      of f;
    - on ``[0.990, 1.013]``, rounding changes f by up to about 1.5 near ``a = 0.990``, where f is about -1, so a
      shift along x by ``c_scale*c`` can change the sign of ``f(a)``, while the conditions require a range of ``c``
      of a minimum width in which ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0``.

    ``10.0**14*(x - 1)**7`` has no terms that cancel.

    With ``modified = 1``, the modification changes what the test problem tests, on both intervals: the source writes
    the polynomial term by term because the polynomial is difficult to evaluate accurately in that form, while
    ``10.0**14*(x - 1)**7`` is not difficult to evaluate accurately.
    """

    number = (1, 3, 1, 17)
    name = "p18"
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
        location="p18",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``10.0**14*(x - c_scale*c - 1)**7``. Category 1 states the rule for
        ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 1:
            return 10.0**14 * (x - 1) ** 7
        else:
            return 10.0**14 * (
                1.0 * x**7 - 7.0 * x**6 + 21.0 * x**5 - 35.0 * x**4 + 35.0 * x**3 - 21.0 * x**2 + 7.0 * x - 1.0
            )

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"), rows=((0.988, 1.012, 0.024, 0.0), (0.99, 1.013, 0.023, 0.0))
            ),
            ParamTable(
                names=("a", "b", "c_scale", "modified"), rows=((0.988, 1.012, 0.024, 1.0), (0.99, 1.013, 0.023, 1.0))
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024, "modified": 0.0},
            x=0.9952,
            c=0.0,
            expected=-0.005870683422720227,
            atol=40.0,
        ),
        FormulaTestCase.value(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024, "modified": 0.0},
            x=0.9952,
            c=0.25,
            expected=-1.7138242687795553,
            atol=40.0,
        ),
        FormulaTestCase.value(
            params={"a": 0.99, "b": 1.013, "c_scale": 0.023, "modified": 0.0},
            x=0.9969,
            c=0.0,
            expected=-0.00027512614110999483,
            atol=40.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024, "modified": 0.0}, expected=(0.988, 1.012)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.99, "b": 1.013, "c_scale": 0.023, "modified": 0.0}, expected=(0.99, 1.013)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024, "modified": 1.0}, expected=(0.988, 1.012)
        ),
        FormulaTestCase.value(
            params={"a": 0.988, "b": 1.012, "c_scale": 0.024, "modified": 1.0},
            x=0.9952,
            c=0.25,
            expected=-1.7138242687795553,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.99, "b": 1.013, "c_scale": 0.023, "modified": 1.0}, expected=(0.99, 1.013)
        ),
        FormulaTestCase.value(
            params={"a": 0.99, "b": 1.013, "c_scale": 0.023, "modified": 1.0},
            x=0.9969,
            c=0.25,
            expected=-0.42520943728900457,
        ),
    )
