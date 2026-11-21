"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f42`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class GanchovskiSmithRackauckasTomovTraykov2026F42(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``(x^2 - x - 6)*(x^2 - 3*x + 2)``; the formula's intervals are `[0, pi]`;
    `[0, 4]` (`Test Functions.pdf`).

    The value ``pi`` is rounded to 12 significant digits, the most that a parameter value holds.

    `Test Functions.pdf` gives the interval `[0, 4]`.
    """

    number = (1, 1, 13, 12)
    name = "f42"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Proektsoft-EOOD/ModAB-Root-Finding."
        ),
        location="f42",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x**2 - x - 6) * (x**2 - 3 * x + 2)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("a", "b", "c_scale"), rows=((0.0, 3.14159265359, 3.14), (0.0, 4.0, 4.0))),)

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14}, x=0.942478, c=0.0, expected=-0.36828251535970846
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14}, x=0.942478, c=0.25, expected=-9.520157703752249
        ),
        FormulaTestCase.value(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, x=1.2, c=0.0, expected=0.9215999999999999),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 3.14159265359, "c_scale": 3.14}, expected=(0.0, 3.14159265359)
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, expected=(0.0, 4.0)),
    )
