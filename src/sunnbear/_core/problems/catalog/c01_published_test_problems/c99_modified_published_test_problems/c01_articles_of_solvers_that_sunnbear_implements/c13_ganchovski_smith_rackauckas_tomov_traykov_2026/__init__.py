"""This category holds the modified formulas of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f04_f27, f05_f29, f19_f75, f21_f81


class ModifiedGanchovskiSmithRackauckasTomovTraykov2026(FormulaCategory):
    """`ModifiedGanchovskiSmithRackauckasTomovTraykov2026` is the category of the modified formulas of 1 publication.

    Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to the modified
    Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. https://doi.org/10.3390/a19050332.
    Supplementary materials: https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder `MDPI-Algorithms-
    Data` of the authors' repository https://github.com/Proektsoft-EOOD/ModAB-Root-Finding.
    """

    number = (1, 99, 1, 13)
    name = "Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026)"
