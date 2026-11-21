"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f92`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class GanchovskiSmithRackauckasTomovTraykov2026F92(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``x^3 - 0.001``; the formula's interval is ``[-10, 10]``.

    `Test Functions.pdf` names it Nearly asymmetric function; the C# code names it Near symmetric function, and §4.2 of
    the article calls it a nearly symmetrical function. §4.2 also solves it on `[-10, 10]` and plots it in Figure 2, and
    Table 1 gives the iterations at which the original and the proposed modAB switch modes and stop. `Test
    Functions.pdf` writes the interval in its root line as `[-0;10]`; its plot spans `[-10, 10]`.
    """

    number = (1, 1, 13, 30)
    name = "f92"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        location="f92",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        return x**3 - 0.001

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-4.0, c=0.0, expected=-64.001),
        FormulaTestCase.value(params={}, x=-4.0, c=0.25, expected=-729.001),
        FormulaTestCase.interval_bounds(params={}, expected=(-10.0, 10.0)),
    )
