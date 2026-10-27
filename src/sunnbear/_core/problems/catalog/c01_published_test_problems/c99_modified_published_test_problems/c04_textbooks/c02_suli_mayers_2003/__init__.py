"""This category holds the modified formulas of Süli, Mayers (2003)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1_2, f05_1_33


class ModifiedSuliMayers2003(FormulaCategory):
    """`ModifiedSuliMayers2003` is the category of the modified formulas of 1 publication.

    Süli, E., Mayers, D. F. (2003). An Introduction to Numerical Analysis. Cambridge University Press, Cambridge.
    https://doi.org/10.1017/CBO9780511801181.
    """

    number = (1, 99, 4, 2)
    name = "Süli, Mayers (2003)"
