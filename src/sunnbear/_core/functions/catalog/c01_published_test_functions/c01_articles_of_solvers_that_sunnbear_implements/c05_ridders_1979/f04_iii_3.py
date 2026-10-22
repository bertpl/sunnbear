"""This module holds the formula of III.3 in Ridders (1979).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1979_ridders`, never this file.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "1c76d8364a3e04f7"


class Ridders1979Iii3(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``sin(pi*x/180)``; the formula's interval is ``[10, 280]``.

    `x` is in degrees, so the root is `180`. The article prints `sin x`; `f` converts `x` from degrees to radians. The
    article calls it a trivial example. sunnbear's `test_paper.py` writes it as `sin(radians(x))`.
    """

    number = (1, 1, 5, 4)
    name = "III.3"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ridders, C. J. F. (1979). A new algorithm for computing a single root of a real continuous"
            " function. IEEE Transactions on Circuits and Systems 26(11), 979–980. "
            "https://doi.org/10.1109/TCS.1979.1084580."
        ),
        location="III.3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 270.0 * c
        return math.sin(math.pi * x / 180)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (10.0, 280.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=91.0, c=0.0, expected=0.9998476951563913),
        FormulaTestCase.value(params={}, x=91.0, c=0.25, expected=0.3987490689252462),
        FormulaTestCase.interval_bounds(params={}, expected=(10.0, 280.0)),
    )
