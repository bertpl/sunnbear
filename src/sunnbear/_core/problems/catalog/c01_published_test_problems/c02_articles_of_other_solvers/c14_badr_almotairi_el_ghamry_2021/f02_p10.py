"""This module holds a formula of Badr, Almotairi, El Ghamry (2021).

The formula comes from the row with the key ``P10`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class BadrAlmotairiElGhamry2021P10(Formula):
    """This formula comes from Badr, Almotairi, El Ghamry (2021).

    The survey writes the source's function as ``x*cos(x) + 1``; the formula's interval is ``[-2, 4]``.
    """

    number = (1, 2, 14, 2)
    name = "P10"
    params = ()
    source = FormulaSource(
        reference=(
            "Badr, E., Almotairi, S., El Ghamry, A. (2021). A comparative study among new hybrid root "
            "finding algorithms and traditional methods. Mathematics 9(11), 1306. "
            "https://doi.org/10.3390/math9111306."
        ),
        location="P10",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 6.0 * c
        return x * math.cos(x) + 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.2, c=0.0, expected=0.8039866844317517),
        FormulaTestCase.value(params={}, x=-0.2, c=0.25, expected=1.2190356403023919),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 4.0)),
    )
