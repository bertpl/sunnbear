"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``26–27`` in the survey of published test problems. The survey describes
this function in words, not as 1 expression, so a person writes this module: a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class RootsFortran20252627(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The survey writes the source's function as ``x/exp(1.0/(x*x))`` (x != 0); ``0.0`` (x = 0); the formula's intervals
    are ``[-1, 4]`` (26), ``[-1.1234, 4.4567]`` (27).

    The comment on the root 0 says it is "just almost impossible to get".
    """

    number = (1, 3, 3, 4)
    name = "26–27"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Williams, J., roots-fortran, file `test/root_tests.f90` at commit `390e7ea` (2025-01-25, "
            "the last commit to the file), "
            "https://github.com/jacobwilliams/roots-fortran/blob/390e7ea30751fe2ab23ddb876a3563e07bef1b76/test/root_tests.f90,"
            " BSD-3-Clause license.\n"
            "\n"
            "The program's header comment gives 1 reference, without naming cases: Alefeld, G. E., "
            'Potra, F. A. and Shi, Y., "Algorithm 748: Enclosing Zeros of Continuous Functions", ACM '
            "Trans. Math. Softw. 21(3), September 1995, pp. 327–344 (no DOI in the file).\n"
            "\n"
            "Comments name these sources for cases or blocks, as they give them:\n"
            '- "Dowell & Jarratt", with no year (cases 18–24).\n'
            '- "Gottlieb\'s paper [table 1 & 2]", with no further detail (cases 30–36). This is Gottlieb'
            " & Thompson (2010), whose rows are in `2010_gottlieb`; cases 30–36 are its tests 1–7, "
            "unchanged.\n"
            "- http://www.mth.pdx.edu/~daescu/mth451_551/Muller_bisection.pdf (cases 41, 42). The host "
            "is gone, and no web archive captured the file.\n"
            '- Alefeld–Potra–Shi (1995), "case 11 from Algorithm 748" (case 45).\n'
            '- Chandrupatla, T. R., "A new hybrid quadratic/bisection algorithm for finding the zero of'
            ' a nonlinear function without using derivatives", Advances in Engineering Software 28(3), '
            "April 1997, pp. 145–149 (cases 47–62).\n"
            '- "A modified three-point Secant method with improved rate and characteristics of '
            'convergence", July 2019, with no author (cases 63–68). This is Tiruneh (2019), whose rows '
            "are in `2019_tiruneh`; cases 63–68 are 6 of the 7 functions of its Table 1. The article "
            "gives starting points, not intervals, so the brackets are roots-fortran's own.\n"
            '- Popovski, D., "A note on King\'s method F for finding a bracketed root", 1982, '
            "https://www.semanticscholar.org/paper/A-note-on-King's-method-F-for-finding-a-bracketed-Popovski/513ffdb3befbf48c38bb70dbec60934472cc9903"
            " (cases 73–98). No file in `sources/` gives the article's rows.\n"
            '- "Stage paper", with "see also #26" (cases 99–102). This is Stage (2013), whose rows are '
            "in `2013_stage`. Case 99 is Stage's §3.5 with its sign flipped, case 100 is §3.6 and case "
            '102 is §3.10; case 101 is no Stage function, but Galdino\'s `g21`–`g23`. "see also #26" '
            "points to no Stage function: case 26 is Brent (1971)'s `x*exp(-x^-2)`.\n"
            '- "P1 in BlendTF paper" (cases 103–117). This is Badr, Almotairi & El Ghamry (2021), whose'
            " rows are in `2021_badr`. Cases 103–117 are all 15 of its problems `P1`–`P15`, not only "
            "`P1`; the only difference is the interval of `P3`, which is `[3, 4]` in the article and "
            "`[3, 7]` in case 105.\n"
            "- Wikipedia, ITP method, "
            "https://en.wikipedia.org/wiki/ITP_method#Example:_Finding_the_root_of_a_polynomial (case "
            "118). Its rows are in `2025_wikipedia_itp_method`, whose function matches case 118.\n"
            '- "the ITP paper : Table 1" (cases 119–127).\n'
            '- "Table 1 from RBP paper" (cases 134–144). This is Suhadolnik (2012), whose rows are in '
            "`2012_suhadolnik`. Cases 134–137 and 140–144 are the examples 1, 2, 3, 5, 7, 8, 10, 17 and"
            " 18 of its Table 1, unchanged; cases 138–139 hold Stage's §3.7, not a Suhadolnik function."
            "\n"
            '- "Zhang test case" (case 145). This is Zhang (2011), whose rows are in `2011_zhang`; the '
            "case's bracket is `[0, 4]`, the interval at which Zhang's Table 1 starts.\n"
            "- http://sergiogaldino.pbworks.com/w/file/fetch/66011429/0130-1943543, the file of Galdino"
            ' (2011) (`2011_galdino`), and "Root-test-functions.pdf : '
            'https://www.researchgate.net/publication/373922895_Additional_test_functions" (cases '
            "146–157).\n"
            '  - That PDF is the 2023 version of Ganchovski\'s "Root-finding Test Functions", whose '
            "revision of 2026-09-29 is `ganchovski_test_functions`.\n"
            "  - Cases 146–157 are its f01, f02, f04, f28–f32, f41 and f42, with f42 split over cases "
            "155–157, and follow the PDF where it differs from the C# code of Tomov & Ganchovski's "
            "benchmark (`2026_tomov_ganchovski_benchmark`).\n"
            "  - The brackets of 4 cases differ: case 146 starts at 0.51, as roots-fortran's own "
            "comment explains, and cases 155–157 bracket each root of f42 in place of `[0, 4]`."
        ),
        location="26–27",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        # below 1e-100, float64 rounds x/exp(1/(x*x)) to 0, and x*x underflows to 0, so that 1/(x*x) divides by 0
        if abs(x) < 1e-100:
            return 0.0
        else:
            return x / math.exp(1.0 / (x * x))

    def interval_bounds(self, a: float, b: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b"),
                rows=(
                    (
                        -1.0,
                        4.0,
                    ),
                    (
                        -1.1234,
                        4.4567,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.5, c=0.0, expected=0.00915781944436709),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.5, c=0.25, expected=-0.12675998655454956),
        FormulaTestCase.value(params={"a": -1.1234, "b": 4.4567}, x=0.55063, c=0.0, expected=0.020345061698967323),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.value(params={"a": -1.0, "b": 4.0}, x=1e-200, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 4.0}, expected=(-1.0, 4.0)),
        FormulaTestCase.interval_bounds(params={"a": -1.1234, "b": 4.4567}, expected=(-1.1234, 4.4567)),
    )
