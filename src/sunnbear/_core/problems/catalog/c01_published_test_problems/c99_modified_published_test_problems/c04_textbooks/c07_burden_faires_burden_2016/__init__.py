"""This category holds the modified versions of the formulas of Burden, Faires, Burden (2016)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_2_2_ex_1, f09_2_1_1, f19_2_1_8, f43_2_4_1_c, f47_2_4_2_c, f48_2_4_2_d


class ModifiedBurdenFairesBurden2016(FormulaCategory):
    """`ModifiedBurdenFairesBurden2016` holds the modified versions of the formulas of 1 publication.

    Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. Cengage Learning, Boston, MA.
    ISBN 978-1-305-25366-7. The copyright page gives © 2016 and the print year 2014.
    """

    number = (1, 99, 4, 7)
    name = "Burden, Faires, Burden (2016)"
