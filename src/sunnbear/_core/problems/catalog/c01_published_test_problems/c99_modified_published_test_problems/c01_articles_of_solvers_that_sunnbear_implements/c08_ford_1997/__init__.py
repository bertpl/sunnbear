"""This category holds the modified formulas of Ford (1997)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_1


class ModifiedFord1997(FormulaCategory):
    """`ModifiedFord1997` is the category of the modified formulas of 1 publication.

    Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia Iranica 4(1&2),
    28–34. The article has no working DOI: the journal's page,
    https://scientiairanica.sharif.edu/article_21758.html, lists 10.24200/sci.2020.21758, which doi.org does not
    resolve. An earlier version is the University of Essex technical report CSM-257 (1995).
    """

    number = (1, 99, 1, 8)
    name = "Ford (1997)"
