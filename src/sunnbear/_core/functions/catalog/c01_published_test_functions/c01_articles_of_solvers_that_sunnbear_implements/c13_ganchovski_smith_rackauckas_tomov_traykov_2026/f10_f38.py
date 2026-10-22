"""This module holds the formula of f38, f39 in Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2026_ganchovski_et_al`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "1d2460ee04bf6e48"


class GanchovskiSmithRackauckasTomovTraykov2026F38(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints 1 function with other parameter values in 2 rows, which the formula writes as ``if(x <= 1/3; -d; 1
    - d)``:

    - f38: ``if(x <= 1/3; -0.5; 0.5)``; the formula's interval is ``[-11, 9]``, with ``d = 0.5``
    - f39: ``if(x <= 1/3; -10^-3; 1 - 10^-3)``; the formula's interval is ``[-11, 9]``, with ``d = 10^-3``
    """

    number = (1, 1, 13, 10)
    name = "f38"
    param_names = ("d",)
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L., Traykov, A. (2026). Improvements to "
            "the modified Anderson–Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. "
            "https://doi.org/10.3390/a19050332. Supplementary materials: "
            "https://www.mdpi.com/article/10.3390/a19050332/s1, also in the folder "
            "`MDPI-Algorithms-Data` of the authors' repository "
            "https://github.com/Just-A-Random-Geek/ModAB-Root-Finding."
        ),
        location="f38, f39",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 20.0 * c
        return (-d) if (x) <= (1 / 3) else (1 - d)

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-11.0, 9.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("d",), rows=((0.5,), (0.001,))),)

    cases = (
        FormulaTestCase.value(params={"d": 0.5}, x=-5.0, c=0.0, expected=-0.5),
        FormulaTestCase.value(params={"d": 0.5}, x=-5.0, c=0.25, expected=-0.5),
        FormulaTestCase.value(params={"d": 0.001}, x=-5.0, c=0.0, expected=-0.001),
        FormulaTestCase.interval_bounds(params={"d": 0.5}, expected=(-11.0, 9.0)),
    )
