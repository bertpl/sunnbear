"""This category holds the formulas of Chen, Li (2007)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_example_1, f02_example_2, f03_example_4


class ChenLi2007(FormulaCategory):
    """`ChenLi2007` is the category of the formulas of 1 publication."""

    number = (1, 2, 6)
    name = "Chen, Li (2007)"
    description = "The test problems come from the article that introduces an improved exponential regula falsi method."
    publication = Publication(
        citation=(
            "Chen, J., Li, W. (2007). An improved exponential regula falsi methods with quadratic convergence of"
            " both diameter and point for solving nonlinear equations. Applied Numerical Mathematics 57(1),"
            " 80–88. Published online 14 February 2006. https://doi.org/10.1016/j.apnum.2006.01.001. The article"
            " prints the volume and the year 2007 but no issue number; the issue number is Crossref's. The survey"
            " lists the article under 2006, the year of the online date that the article prints; the issue is"
            " dated 2007."
        ),
        citation_key="Chen07",
        authors=("Chen, J.", "Li, W."),
        year=2007,
        title=(
            "An improved exponential regula falsi methods with quadratic convergence of both diameter and "
            "point for solving nonlinear equations"
        ),
        published_in="Applied Numerical Mathematics",
        doi="10.1016/j.apnum.2006.01.001",
    )
