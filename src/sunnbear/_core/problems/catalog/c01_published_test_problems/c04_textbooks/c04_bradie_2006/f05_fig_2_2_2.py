"""This module holds a formula of Bradie (2006).

The formula comes from the row with the key ``Fig. 2.2#2`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe
from sunnbear._core.utils.math_functions import real_root


class Bradie2006Fig222(Formula):
    """This formula comes from Bradie (2006).

    The survey writes the source's function as ``(x - 1)^(1/7)``; the formula's interval is `[0, 2]` (Fig. 2.2).

    Root 1; the real 7th root. Figure only, plotted on `[0, 2]`: nearly vertical at the root, so `x` within `1E-7` of it
    still gives `f` about `1E-1`.
    """

    number = (1, 4, 4, 5)
    name = "Fig. 2.2#2"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Bradie, B. (2006). A Friendly Introduction to Numerical Analysis. Pearson Prentice Hall, "
            "Upper Saddle River, NJ. ISBN 0-13-013054-0."
        ),
        location="Fig. 2.2#2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return real_root((x - 1), 7)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-0.8773066621237415),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-0.9850612054411155),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
