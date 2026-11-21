"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P14`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BadrAlmotairiElGhamry2021P14(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``exp(x) - 3*x - 2``; the formula's interval is ``[2, 3]``.
    """

    number = (1, 2, 14, 5)
    name = "P14"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Badr, E., Almotairi, S., El Ghamry, A. (2021). A comparative study among new hybrid root "
            "finding algorithms and traditional methods. Mathematics 9(11), 1306. "
            "https://doi.org/10.3390/math9111306."
        ),
        location="P14",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return math.exp(x) - 3 * x - 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=1.0741824548147194),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=-0.382098893693229),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
