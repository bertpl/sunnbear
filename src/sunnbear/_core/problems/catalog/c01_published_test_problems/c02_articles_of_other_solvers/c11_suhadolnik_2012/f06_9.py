"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``9`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Suhadolnik20129(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``(x - 1)^3 - 1``; the formula's interval is ``[1.5, 3]``.
    """

    number = (1, 2, 11, 6)
    name = "9"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Suhadolnik, A. (2012). Combined bracketing methods for solving nonlinear equations. "
            "Applied Mathematics Letters 25(11), 1755–1760. https://doi.org/10.1016/j.aml.2012.02.006."
        ),
        location="9",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return (x - 1) ** 3 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.5, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=1.95, c=0.0, expected=-0.1426250000000001),
        FormulaTestCase.value(params={}, x=1.95, c=0.25, expected=-0.8098906250000001),
        FormulaTestCase.interval_bounds(params={}, expected=(1.5, 3.0)),
    )
