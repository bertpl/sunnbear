"""This category holds the formulas of Foo, Tan (2025)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_4_2, f02_section_4_3_1


class FooTan2025(FormulaCategory):
    """`FooTan2025` is the category of the formulas of 1 publication."""

    number = (1, 2, 15)
    name = "Foo, Tan (2025)"
    description = (
        "The test problems come from a preprint that introduces a higher-order root-finding method "
        "and applies it to entropy functions."
    )
    publication = Publication(
        citation=(
            "Foo, W. G., Tan, C. H. (2025). Higher-Order Root-Finding Algorithm and its Applications. arXiv"
            " preprint 2509.20897v1. https://doi.org/10.48550/arxiv.2509.20897"
            " (https://arxiv.org/abs/2509.20897v1)."
        ),
        citation_key="Foo25",
        authors=("Foo, W. G.", "Tan, C. H."),
        year=2025,
        title="Higher-Order Root-Finding Algorithm and its Applications",
        published_in="arXiv",
        doi="10.48550/arxiv.2509.20897",
    )
