"""This category holds the modified formulas of Burkardt (2016)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_p04, f06_p06, f12_p12, f17_p18


class ModifiedBurkardt2016(FormulaCategory):
    """`ModifiedBurkardt2016` is the category of the modified formulas of 1 publication.

    John Burkardt, TEST_ZERO, Python version, file `test_zero.py`,
    https://people.sc.fsu.edu/~jburkardt/py_src/test_zero/test_zero.py, MIT license.

    The file is unversioned and has no file header; the rows come from the version with sha256
    `658ed0a0b520eba30e87d4a08d73b444fe4f3edf14a8a94339703eca2ef9680c`. The comment of each function gives the date
    on which that function was last modified, and the latest is 16 October 2020, for `p16_root`. The year is 2016
    because every function that the rows transcribe (`pNN_fx`, `pNN_rang`, `pNN_start` and `pNN_title`) is dated 2
    December 2016 or earlier.

    The file cites sources for 3 of its functions, and names a 4th origin without a reference: - [1] George Donovan,
    Arnold Miller, Timothy Moreland, "Pathological Functions for Newton's Method", American   Mathematical Monthly,
    January 1993, pages 53-58 (no DOI in the file), for `p15`. - [2] Peter Colwell, Solving Kepler's Equation Over
    Three Centuries, Willmann-Bell, 1993, and [3] Jean Meeus,   Astronomical Algorithms, Willman-Bell, 1991, for
    `p16`. - [4] Cleve Moler, Numerical Computing with MATLAB, SIAM, 2004, ISBN 978-0-898716-60-3, for `p18`. -
    `p17`'s comment says that Wallis used the function to illustrate Newton's method, with no reference.

    The file's `brent` solver cites Brent's 1973 book for the algorithm, not for any function.
    """

    number = (1, 99, 3, 1)
    name = "Burkardt (2016)"
