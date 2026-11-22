"""This category holds the modified versions of the formulas of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_f27, f05_f29, f11_f40, f19_f75, f21_f81


class ModifiedGanchovskiSmithRackauckasTomovTraykov2026(FormulaCategory):
    """`ModifiedGanchovskiSmithRackauckasTomovTraykov2026` holds the modified versions of the formulas of 1 publication.

    Its formulas modify those of category 1.1.13, `GanchovskiSmithRackauckasTomovTraykov2026`, and come from its
    publication.
    """

    number = (1, 99, 1, 13)
    name = "Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026)"
    description = (
        "The test problems are modified versions of those that come from the article that improves the "
        "modified Anderson–Björck method."
    )
