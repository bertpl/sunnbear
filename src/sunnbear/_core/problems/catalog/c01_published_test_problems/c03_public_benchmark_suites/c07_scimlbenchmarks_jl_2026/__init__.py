"""This category holds the formulas of SciMLBenchmarks.jl (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_function_g, f02_function_6


class ScimlbenchmarksJl2026(FormulaCategory):
    """`ScimlbenchmarksJl2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 7)
    name = "SciMLBenchmarks.jl (2026)"
    description = "The test problems come from the Interval Rootfinding Test Suite of SciMLBenchmarks.jl."
    publication = Publication(
        citation=(
            'SciMLBenchmarks.jl (2026), "Interval Rootfinding Test Suite" by Fabian Gittins (the front matter of'
            " the file), file `benchmarks/IntervalNonlinearProblem/suite.jmd` at commit"
            " `8a67931f726eeb53604926a6dd6bfc750316b4c4`,"
            " https://github.com/SciML/SciMLBenchmarks.jl/blob/8a67931f726eeb53604926a6dd6bfc750316b4c4/benchmarks/IntervalNonlinearProblem/suite.jmd,"
            ' MIT license. The file names no source for its functions; it calls them "a selection of challenging'
            ' test functions from the literature".'
        ),
        citation_key="SciMLBenchmarks26",
        authors=("Fabian Gittins",),
        year=2026,
        title="Interval Rootfinding Test Suite",
        published_in="SciMLBenchmarks.jl",
        url=(
            "https://github.com/SciML/SciMLBenchmarks.jl/blob/8a67931f726eeb53604926a6dd6bfc750316b4c4/benchmarks/IntervalNonlinearProblem/suite.jmd"
        ),
    )
