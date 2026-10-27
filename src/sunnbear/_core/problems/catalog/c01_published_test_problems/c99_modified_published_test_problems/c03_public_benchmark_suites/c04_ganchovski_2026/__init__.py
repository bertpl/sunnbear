"""This category holds the modified formulas of Ganchovski (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_f100


class ModifiedGanchovski2026(FormulaCategory):
    """`ModifiedGanchovski2026` is the category of the modified formulas of 1 publication.

    Ganchovski, N. (2026). Root-finding Test Functions. The file `Test functions.pdf` in the repository
    https://github.com/Proektsoft-EOOD/ModAB-Root-Finding at commit `b3309e9a5177d6305ac84deba6537adb9b878c5e`:
    https://raw.githubusercontent.com/Proektsoft-EOOD/ModAB-Root-
    Finding/b3309e9a5177d6305ac84deba6537adb9b878c5e/Test%20functions.pdf. - The PDF prints no author or date: its
    metadata give 2026-09-29 as its creation date. The repository's README puts   it under the MIT License of
    `C/LICENSE`, which names Ned Ganchovski as the copyright holder. - An earlier version was posted on ResearchGate
    in 2023 as "Additional test functions",
    https://www.researchgate.net/publication/373922895_Additional_test_functions; roots-fortran (`roots_fortran`)
    cites that version.
    """

    number = (1, 99, 3, 4)
    name = "Ganchovski (2026)"
