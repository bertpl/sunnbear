"""This category holds the modified versions of the formulas of Galdino (2011)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_f4, f06_f6


class ModifiedGaldino2011(FormulaCategory):
    """`ModifiedGaldino2011` holds the modified versions of the formulas of 1 publication.

    Galdino, S. (2011). A family of regula falsi root-finding methods. Proceedings of the 2011 World Congress on
    Engineering and Technology, IEEE Press, Shanghai, pp. 514–517. ISBN 978-1-61284-365-0. No DOI; the author's
    copy: http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543.
    """

    number = (1, 99, 2, 9)
    name = "Galdino (2011)"
