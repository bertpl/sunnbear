"""This category holds the modified formulas of Chapra, Canale (2015)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_pt2_3, f02_ex_5_2, f18_prob_5_10, f20_prob_5_15


class ModifiedChapraCanale2015(FormulaCategory):
    """`ModifiedChapraCanale2015` is the category of the modified formulas of 1 publication.

    Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. McGraw-Hill Education, New York,
    NY. ISBN 978-0-07-339792-4. The 8th edition appeared in 2021.
    """

    number = (1, 99, 4, 6)
    name = "Chapra, Canale (2015)"
