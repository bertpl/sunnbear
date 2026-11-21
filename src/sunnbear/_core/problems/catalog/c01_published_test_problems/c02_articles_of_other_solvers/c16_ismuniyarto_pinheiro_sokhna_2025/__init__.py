"""This category holds the formulas of Ismuniyarto, Pinheiro, Sokhna (2025)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_3


class IsmuniyartoPinheiroSokhna2025(FormulaCategory):
    """`IsmuniyartoPinheiroSokhna2025` is the category of the formulas of 1 publication.

    Ismuniyarto, Pinheiro, D., Sokhna, E. H. L. (2025). A numerical study of bracketing root-finding methods for
    nonlinear equations: applications to break-even point determination. Interval: Indonesian Journal of Mathematical
    Education 3(2), 213–218. https://doi.org/10.37251/ijome.v3i2.2782. The first author has a single name.
    """

    number = (1, 2, 16)
    name = "Ismuniyarto, Pinheiro, Sokhna (2025)"
    description = "Test problems from an article that applies bracketing methods to find a break-even point."
