"""This category holds the modified versions of the formulas of Roots.jl (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_func9, f03_func10, f04_func11


class ModifiedRootsJl2026(FormulaCategory):
    """`ModifiedRootsJl2026` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.3.6, `RootsJl2026`, and come from the publication of `RootsJl2026`.
    """

    number = (1, 99, 3, 6)
    name = "Roots.jl (2026)"
    description = (
        "The test problems are modified versions of those that come from the tests of Roots.jl, a Julia "
        "package of root finders, version 3.0.11."
    )
