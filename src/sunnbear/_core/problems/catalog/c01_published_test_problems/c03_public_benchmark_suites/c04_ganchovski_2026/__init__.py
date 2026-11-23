"""This category holds the formulas of Ganchovski (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_f93, f02_function_f100, f03_function_f101


class Ganchovski2026(FormulaCategory):
    """`Ganchovski2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 4)
    name = "Ganchovski (2026)"
    description = (
        "The test problems come from Root-finding Test Functions, the collection of functions in "
        "the repository of the modified Anderson–Björck method."
    )
    publication = Publication(
        citation=(
            "Ganchovski, N. (2026). Root-finding Test Functions. The file `Test functions.pdf` in the repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding at commit "
            "`b3309e9a5177d6305ac84deba6537adb9b878c5e`: https://raw.githubusercontent.com/Proektsoft-EOOD/ModAB-Root-"
            "Finding/b3309e9a5177d6305ac84deba6537adb9b878c5e/Test%20functions.pdf."
        ),
        citation_key="Ganchovski26b",
        authors=("Ganchovski, N.",),
        year=2026,
        title="Root-finding Test Functions",
        url=(
            "https://raw.githubusercontent.com/Proektsoft-EOOD/ModAB-Root-Finding/b3309e9a5177d6305ac84deba6537adb9b878c5e/Test%20functions.pdf"
        ),
    )
