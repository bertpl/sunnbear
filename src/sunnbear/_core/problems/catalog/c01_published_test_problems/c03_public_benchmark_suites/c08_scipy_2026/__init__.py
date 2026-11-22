"""This category holds the formulas of SciPy (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_f1, f02_f2, f03_f3, f04_f4, f05_f5, f06_f6, f07_aps14_f, f08_aps15_f


class Scipy2026(FormulaCategory):
    """`Scipy2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 8)
    name = "SciPy (2026)"
    description = "The test problems come from the module of test problems for SciPy's root finders, release 1.18.1."
    publication = Publication(
        citation=(
            "SciPy 1.18.1, module `scipy/optimize/_tstutils.py`,"
            " https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/_tstutils.py. The module cites 2"
            ' sources:\n- [1] Alefeld, G. E., Potra, F. A. and Shi, Y., "Algorithm 748: Enclosing Zeros of'
            ' Continuous Functions", ACM Trans. Math. Softw. 21(3), September 1995, pp. 327–344,'
            ' https://dl.acm.org/doi/10.1145/210089.210111; the module misprints the volume as "Volume 221" and'
            ' gives no issue or pages\n- [2] Chandrupatla, T. R., "A new hybrid quadratic/bisection algorithm for'
            ' finding the zero of a nonlinear function without using derivatives", Advances in Engineering'
            " Software 28.3 (1997): 145-149 (no DOI in the module)"
        )
    )
