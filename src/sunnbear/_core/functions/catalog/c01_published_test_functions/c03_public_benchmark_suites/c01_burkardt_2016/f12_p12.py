"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p12`` in the survey of published test problems. The survey describes this
function in words, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Burkardt2016P12(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``-exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x < 1.0);
    ``0.0`` (x = 1.0); ``+exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x > 1.0), with the parameters
    ``factor = 1000.0``; the formula's intervals are ``[-4.0, 4.1]`` (rang); ``[0.50, 2.0]`` (starts 2 and 1).

    starts 2.0, 0.50, 4.0
    """

    number = (1, 3, 1, 12)
    name = "p12"
    param_names = ("factor", "a", "b")
    source = FormulaSource(
        reference=(
            "John Burkardt, TEST_ZERO, Python version, file `test_zero.py`, "
            "https://people.sc.fsu.edu/~jburkardt/py_src/test_zero/test_zero.py, MIT license. The file "
            "is unversioned: its header says that it was last modified on 1 December 2016, and the rows"
            " come from the version with sha256 "
            "`658ed0a0b520eba30e87d4a08d73b444fe4f3edf14a8a94339703eca2ef9680c`. The file cites sources"
            " for 3 of its functions, and names a 4th origin without a reference:\n"
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
    def parametrized_fun(x: float, c: float, factor: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        if x < 1.0:
            return -math.exp(math.log(factor) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)
        elif x == 1.0:
            return 0.0
        else:
            return math.exp(math.log(factor) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)

    def interval_bounds(self, factor: float, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("factor", "a", "b"),
                rows=(
                    (
                        1000.0,
                        -4.0,
                        4.1,
                    ),
                    (
                        1000.0,
                        0.5,
                        2.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1}, x=-1.57, c=0.0, expected=-2208.918772196994
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1}, x=-1.57, c=0.25, expected=-4382.445368656935
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": 0.5, "b": 2.0}, x=0.95, c=0.0, expected=-9.575847983576841e-173
        ),
        FormulaTestCase.value(params={"factor": 1000.0, "a": -4.0, "b": 4.1}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={"factor": 1000.0, "a": -4.0, "b": 4.1}, x=1.5, c=0.0, expected=9.15781944436709),
        FormulaTestCase.interval_bounds(params={"factor": 1000.0, "a": -4.0, "b": 4.1}, expected=(-4.0, 4.1)),
        FormulaTestCase.interval_bounds(params={"factor": 1000.0, "a": 0.5, "b": 2.0}, expected=(0.5, 2.0)),
    )
