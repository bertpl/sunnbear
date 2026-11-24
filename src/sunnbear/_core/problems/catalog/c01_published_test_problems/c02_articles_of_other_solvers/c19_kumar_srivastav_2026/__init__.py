"""This category holds the formulas of Kumar, Srivastav (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_f2, f02_function_f3, f03_function_f4, f04_function_f5, f05_function_f6, f06_appendix_a_2


class KumarSrivastav2026(FormulaCategory):
    """`KumarSrivastav2026` is the category of the formulas of 1 publication."""

    number = (1, 2, 19)
    name = "Kumar, Srivastav (2026)"
    description = "The test problems come from a preprint that introduces a randomized bracketing method."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
