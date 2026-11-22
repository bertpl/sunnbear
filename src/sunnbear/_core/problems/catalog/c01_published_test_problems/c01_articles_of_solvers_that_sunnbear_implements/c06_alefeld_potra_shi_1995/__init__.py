"""This category holds the formulas of Alefeld, Potra, Shi (1995)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_4, f02_6, f03_12


class AlefeldPotraShi1995(FormulaCategory):
    """`AlefeldPotraShi1995` is the category of the formulas of 1 publication."""

    number = (1, 1, 6)
    name = "Alefeld, Potra, Shi (1995)"
    description = (
        "The test problems come from the article that introduces Algorithm 748, which encloses "
        "zeros of continuous functions."
    )
    publication = Publication(
        citation=(
            "Alefeld, G. E., Potra, F. A., Shi, Y. (1995). Algorithm 748: enclosing zeros of continuous"
            " functions. ACM Transactions on Mathematical Software 21(3), 327–344."
            " https://doi.org/10.1145/210089.210111. The authors' code is CALGO 748:"
            " https://www.netlib.org/toms/748."
        ),
        citation_key="Alefeld95",
        authors=("Alefeld, G. E.", "Potra, F. A.", "Shi, Y."),
        year=1995,
        title="Algorithm 748: enclosing zeros of continuous functions",
        published_in="ACM Transactions on Mathematical Software",
        doi="10.1145/210089.210111",
    )
