"""This category holds the formulas of Anderson, Björck (1973)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_ex_6


class AndersonBjorck1973(FormulaCategory):
    """`AndersonBjorck1973` is the category of the formulas of 1 publication."""

    number = (1, 1, 3)
    name = "Anderson, Björck (1973)"
    description = (
        "The test problems come from the article that introduces the Anderson–Björck method, a "
        "regula falsi method of high order."
    )
    publication = Publication(
        citation=(
            "Anderson, N., Björck, Å. (1973). A new high order method of regula falsi type for computing a root"
            " of an equation. BIT 13(3), 253–264. https://doi.org/10.1007/BF01951936."
        ),
        citation_key="Anderson73",
        authors=("Anderson, N.", "Björck, Å."),
        year=1973,
        title="A new high order method of regula falsi type for computing a root of an equation",
        published_in="BIT",
        doi="10.1007/BF01951936",
    )
