"""This module holds the formula of §3 in Ganchovski, Traykov (2023).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
2023_ganchovski_traykov`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "d7adb4c3a66a1b53"


class GanchovskiTraykov20233(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``4 - tan(x)``; the formula's interval is ``[0, 1.5]``.

    Not in Table 2; used for the convergence charts of Figures 10 (§3) and 12 (§5). §3 prints the interval as `[0.
    1.5]`.
    """

    number = (1, 1, 10, 1)
    name = "§3"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ganchovski, N., Traykov, A. (2023). Modified Anderson-Bjork's method for solving nonlinear"
            " equations in structural mechanics. IOP Conf. Series: Materials Science and Engineering "
            "1276, 012010. https://doi.org/10.1088/1757-899X/1276/1/012010."
        ),
        location="§3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 1.5 * c
        return 4 - math.tan(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=3.516944934383422),
        FormulaTestCase.value(params={}, x=0.45, c=0.25, expected=3.924859057871715),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
