"""This category holds the formulas of Steffen et al. (2025)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_equation_6, f02_equation_8


class SteffenEtAl2025(FormulaCategory):
    """`SteffenEtAl2025` is the category of the formulas of 1 publication."""

    number = (1, 1, 11)
    name = "Steffen et al. (2025)"
    description = (
        "The test problems come from an article that guarantees a halving of the interval in "
        "Dekker's and Brent's methods."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
