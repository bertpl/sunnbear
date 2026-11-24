"""This category holds the formulas of Tomov, Ganchovski (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_equation_25, f02_function_b, f03_function_c


class TomovGanchovski2026(FormulaCategory):
    """`TomovGanchovski2026` is the category of the formulas of 1 publication."""

    number = (1, 1, 15)
    name = "Tomov, Ganchovski (2026)"
    description = (
        "The test problems come from a preprint on the global convergence and the stopping rule of "
        "a safeguarded modified Anderson–Björck method."
    )
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
