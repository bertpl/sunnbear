"""This category holds the formulas of Li, Zhou, Lange, Tian (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_example_1, f02_example_3, f03_section_7_1, f04_appendix_d, f05_section_7_3


class LiZhouLangeTian2026(FormulaCategory):
    """`LiZhouLangeTian2026` is the category of the formulas of 1 publication."""

    number = (1, 2, 20)
    name = "Li, Zhou, Lange, Tian (2026)"
    description = "The test problems come from the article that introduces the upper-crossing/solution algorithm."
    publication = Publication(
        citation=(
            "Li, X.-J., Zhou, H., Lange, K., Tian, G.-L. (2026). The upper–crossing/solution (US) algorithm with"
            " strongly stable convergence and an acceleration technique for root–finding problems. Statistics and"
            " Computing 36(4), 197. https://doi.org/10.1007/s11222-026-10902-z. Preprint: arXiv 2212.00797v2 (8"
            " November 2025), https://arxiv.org/abs/2212.00797v2. The authors' R code:"
            " https://github.com/Xunjian-Li/US-algorithm.git."
        ),
        citation_key="Li26",
        authors=("Li, X.-J.", "Zhou, H.", "Lange, K.", "Tian, G.-L."),
        year=2026,
        title=(
            "The upper–crossing/solution (US) algorithm with strongly stable convergence and an acceleration "
            "technique for root–finding problems"
        ),
        published_in="Statistics and Computing",
        doi="10.1007/s11222-026-10902-z",
    )
