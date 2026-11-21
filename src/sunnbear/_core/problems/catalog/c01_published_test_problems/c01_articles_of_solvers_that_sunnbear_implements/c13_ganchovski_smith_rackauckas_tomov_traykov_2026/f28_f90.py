"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f90`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class GanchovskiSmithRackauckasTomovTraykov2026F90(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``x^3 - 2*x^2 + x - 0.025``; the formula's interval is ``[-1.0, 2.0]``.
    """

    number = (1, 1, 13, 28)
    name = "f90"
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
        location="f90",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return x**3 - 2 * x**2 + x - 0.025

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.1, c=0.0, expected=-0.14600000000000002),
        FormulaTestCase.value(params={}, x=-0.1, c=0.25, expected=-2.934125),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 2.0)),
    )
