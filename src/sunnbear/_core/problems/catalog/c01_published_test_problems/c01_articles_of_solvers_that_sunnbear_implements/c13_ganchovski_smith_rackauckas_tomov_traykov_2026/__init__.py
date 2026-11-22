"""This category holds the formulas of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_function_f24,
    f02_function_f25,
    f03_function_f26,
    f04_function_f27,
    f05_function_f29,
    f06_function_f34,
    f07_function_f35,
    f08_function_f36,
    f09_function_f37,
    f10_function_f38,
    f11_function_f40,
    f12_function_f42,
    f13_function_f43,
    f14_function_f44,
    f15_function_f45,
    f16_function_f46,
    f17_function_f47,
    f18_function_f49,
    f19_function_f75,
    f20_function_f76,
    f21_function_f81,
    f22_function_f84,
    f23_function_f85,
    f24_function_f86,
    f25_function_f87,
    f26_function_f88,
    f27_function_f89,
    f28_function_f90,
    f29_function_f91,
    f30_function_f92,
)


class GanchovskiSmithRackauckasTomovTraykov2026(FormulaCategory):
    """`GanchovskiSmithRackauckasTomovTraykov2026` is the category of the formulas of 1 publication."""

    number = (1, 1, 13)
    name = "Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026)"
    description = "The test problems come from the article that improves the modified Anderson–Björck method."
    publication = Publication(
        citation=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to the"
            " modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332."
            " https://doi.org/10.3390/a19050332. Supplementary materials:"
            " https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder `MDPI-Algorithms-Data` of the"
            " authors' repository https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        citation_key="Ganchovski26a",
        authors=("Ganchovski, N.", "Smith, O.", "Rackauckas, C.", "Tomov, L.", "Traykov, A."),
        year=2026,
        title="Improvements to the modified Anderson–Björck (modAB) root-finding algorithm",
        published_in="Algorithms",
        doi="10.3390/a19050332",
    )
