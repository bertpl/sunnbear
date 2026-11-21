"""This category holds the formulas of Chen, Li (2006)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1, f02_2, f03_4


class ChenLi2006(FormulaCategory):
    """`ChenLi2006` is the category of the formulas of 1 publication.

    Chen, J., Li, W. (2007). An improved exponential regula falsi methods with quadratic convergence of both diameter
    and point for solving nonlinear equations. Applied Numerical Mathematics 57(1), 80–88. Published online 14 February
    2006. https://doi.org/10.1016/j.apnum.2006.01.001. The article prints the volume and the year 2007 but no issue
    number; the issue number is Crossref's. The year 2006 of the title follows the online date that the article prints;
    the issue is dated 2007.
    """

    number = (1, 2, 6)
    name = "Chen, Li (2006)"
    description = "Test problems from the article that introduces an improved exponential regula falsi method."
