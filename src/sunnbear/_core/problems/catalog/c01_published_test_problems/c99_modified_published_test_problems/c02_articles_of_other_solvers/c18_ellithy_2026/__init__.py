"""This category holds the modified formulas of Ellithy (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f05_20, f06_21, f14_30, f20_38


class ModifiedEllithy2026(FormulaCategory):
    """`ModifiedEllithy2026` is the category of the modified formulas of 1 publication.

    Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root finding. Journal of the
    Egyptian Mathematical Society 34(1), 91–115. https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the
    author's repository https://github.com/Abdelrhman-Ellithy/hybridroots, at commit
    `7f22131ef4e1def3e3928dc6558f46f756d0a5ea`.
    """

    number = (1, 99, 2, 18)
    name = "Ellithy (2026)"
