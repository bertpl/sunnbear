"""`FormulaSource` records the publication that a formula comes from."""

from dataclasses import dataclass


# ==================================================================================================
#  FormulaSource
# ==================================================================================================
@dataclass(frozen=True)
class FormulaSource:
    """`FormulaSource` names the publication of a formula, and where in that publication the formula appears.

    Attributes:
        reference: The publication's full reference, with its DOI or URL.
        location: Where in the publication the formula appears, such as "Table 2" or "Prob. 5.18".
    """

    reference: str
    location: str
