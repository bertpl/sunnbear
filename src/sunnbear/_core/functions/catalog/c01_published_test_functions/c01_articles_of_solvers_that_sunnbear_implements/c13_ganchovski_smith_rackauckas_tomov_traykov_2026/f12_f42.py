"""This module holds the formula of f42 in Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2026_ganchovski_et_al`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "a12e09ff4b25510b"


class GanchovskiSmithRackauckasTomovTraykov2026F42(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``(x^2 - x - 6)*(x^2 - 3*x + 2)``; the formula's interval is `[0, pi]`; `[0, 4]` (TF).

    The bounds ``pi`` are rounded to 12 significant digits, the most that a parameter value holds.

    TF gives the interval `[0, 4]`.
    """

    number = (1, 1, 13, 12)
    name = "f42"
    param_names = ("a", "b")
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Just-A-Random-Geek/ModAB-Root-Finding."
        ),
        location="f42",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - (b - a) * c
        return (x**2 - x - 6) * (x**2 - 3 * x + 2)

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
                        0.0,
                        3.14159265359,
                    ),
                    (
                        0.0,
                        4.0,
                    ),
                ),
            ),
        )

    cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 3.14159265359}, x=0.942478, c=0.0, expected=-0.36828251535970846),
        FormulaTestCase.value(params={"a": 0.0, "b": 3.14159265359}, x=0.942478, c=0.25, expected=-9.526291078166064),
        FormulaTestCase.value(params={"a": 0.0, "b": 4.0}, x=1.2, c=0.0, expected=0.9215999999999999),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 3.14159265359}, expected=(0.0, 3.14159265359)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 4.0}, expected=(0.0, 4.0)),
    )
