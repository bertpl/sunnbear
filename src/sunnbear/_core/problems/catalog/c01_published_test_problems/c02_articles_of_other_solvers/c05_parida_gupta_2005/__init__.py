"""This category holds the formulas of Parida, Gupta (2005)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1, f02_2, f03_4


class ParidaGupta2005(FormulaCategory):
    """`ParidaGupta2005` is the category of the formulas of 1 publication.

    Parida, P. K., Gupta, D. K. (2006). An improved regula-falsi method for enclosing simple zeros of nonlinear
    equations. Applied Mathematics and Computation 177(2), 769–776. https://doi.org/10.1016/j.amc.2005.11.034. The
    article prints the volume and the year 2006 but no issue number; the issue number is Crossref's. The year 2005 of
    the title follows the article's copyright line, "© 2005 Elsevier Inc.", which is also the year in the DOI; the
    article prints no online date.
    """

    number = (1, 2, 5)
    name = "Parida, Gupta (2005)"
    description = "Test problems from the article that introduces an improved regula falsi method."
