"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P7`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BadrAlmotairiElGhamry2021P7(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``x*exp(x) - 7``; the formula's interval is ``[0, 2]``.
    """

    number = (1, 2, 14, 1)
    name = "P7"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Badr, E., Almotairi, S., El Ghamry, A. (2021). A comparative study among new hybrid root "
            "finding algorithms and traditional methods. Mathematics 9(11), 1306. "
            "https://doi.org/10.3390/math9111306."
        ),
        location="P7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x * math.exp(x) - 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.6, c=0.0, expected=-5.906728719765694),
        FormulaTestCase.value(params={}, x=0.6, c=0.25, expected=-6.889482908192435),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 2.0)),
    )
