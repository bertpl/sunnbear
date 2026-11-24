"""This category holds the formulas of Ismuniyarto, Pinheiro, Sokhna (2025)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_section_3


class IsmuniyartoPinheiroSokhna2025(FormulaCategory):
    """`IsmuniyartoPinheiroSokhna2025` is the category of the formulas of 1 publication."""

    number = (1, 2, 16)
    name = "Ismuniyarto, Pinheiro, Sokhna (2025)"
    description = "The test problems come from an article that applies bracketing methods to find a break-even point."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
