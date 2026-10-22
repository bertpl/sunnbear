"""This module holds the formula of Table 1 in Dowell, Jarratt (1971).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1971_dowell_jarratt_illinois`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# The fingerprint of the survey fields that this module is generated from; the tests compare it with
# the survey, so that a module left stale after a change of the survey fails them.
SURVEY_FINGERPRINT = "d32e45cc60268183"


class DowellJarratt1971Table1(Formula):
    """`DowellJarratt1971Table1` evaluates the published function at ``x - (b - a)*c``.

    The source prints ``sin(x) - 0.5``; the formula's interval is ``[0, 1.5]``.

    Root `pi/6`. Starting values `x0 = 0.0`, `x1 = 1.5`.
    """

    number = (1, 1, 1, 1)
    name = "Table 1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Dowell, M., Jarratt, P. (1971). A modified regula falsi method for computing the root of "
            "an equation. BIT 11(2), 168–174. https://doi.org/10.1007/BF01934364."
        ),
        location="Table 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``."""
        x = x - 1.5 * c
        return math.sin(x) - 0.5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=0.45, c=0.0, expected=-0.06503446588876978),
        FormulaTestCase.value(params={}, x=0.45, c=0.25, expected=-0.42507029272725766),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.5)),
    )
