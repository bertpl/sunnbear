"""This category holds the formulas of SciMLBenchmarks.jl (2026)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_g, f02_function_6


class ScimlbenchmarksJl2026(FormulaCategory):
    """`ScimlbenchmarksJl2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 7)
    name = "SciMLBenchmarks.jl (2026)"
    description = "The test problems come from the Interval Rootfinding Test Suite of SciMLBenchmarks.jl."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
