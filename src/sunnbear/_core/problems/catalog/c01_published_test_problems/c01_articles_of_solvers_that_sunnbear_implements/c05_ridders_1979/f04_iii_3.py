"""This module holds a formula of Ridders (1979).

The formula comes from the row with the key ``III.3`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Ridders1979Iii3(Formula):
    """This formula comes from Ridders (1979).

    The survey writes the source's function as ``sin(pi*x/180)``; the formula's interval is ``[10, 280]``.

    `x` is in degrees, so the root is `180`. The article prints `sin x`; the formula converts `x` from degrees to
    radians. The article calls it a trivial example. sunnbear's `tests/solvers/bracketing/ridders/test_paper.py` writes
    it as `sin(radians(x))`.
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
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 270.0 * c
        return math.sin(math.pi * x / 180)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (10.0, 280.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=91.0, c=0.0, expected=0.9998476951563913),
        FormulaTestCase.value(params={}, x=91.0, c=0.25, expected=0.3987490689252462),
        FormulaTestCase.interval_bounds(params={}, expected=(10.0, 280.0)),
    )
