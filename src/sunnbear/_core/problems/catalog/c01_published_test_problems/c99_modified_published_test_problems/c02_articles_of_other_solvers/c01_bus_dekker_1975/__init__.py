"""This category holds the modified versions of the formulas of Bus, Dekker (1975)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f05_iii, f06_iv


class ModifiedBusDekker1975(FormulaCategory):
    """`ModifiedBusDekker1975` holds the modified versions of the formulas of 1 publication.

    Bus, J. C. P., Dekker, T. J. (1975). Two efficient algorithms with guaranteed convergence for finding a zero of a
    function. ACM Transactions on Mathematical Software 1(4), 330–345. https://doi.org/10.1145/355656.355659.
    """

    number = (1, 99, 2, 1)
    name = "Bus, Dekker (1975)"
