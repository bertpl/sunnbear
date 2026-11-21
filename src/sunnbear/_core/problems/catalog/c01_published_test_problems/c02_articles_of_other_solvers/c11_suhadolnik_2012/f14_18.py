"""This module holds a formula of Suhadolnik (2012).

The formula comes from the row with the key ``18`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Suhadolnik201218(Formula):
    """This formula comes from Suhadolnik (2012).

    The survey writes the source's function as ``x^5``; the formula's interval is ``[-0.5, 1/3]``.

    Section 4 names examples 17 and 18 as cases where `f'(x*) = 0`, on which the methods may converge slowly.
    """

    number = (1, 2, 11, 14)
    name = "18"
    params = ()
    source = FormulaSource(
        reference=(
            "Suhadolnik, A. (2012). Combined bracketing methods for solving nonlinear equations. "
            "Applied Mathematics Letters 25(11), 1755–1760. https://doi.org/10.1016/j.aml.2012.02.006."
        ),
        location="18",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.833 * c
        return x**5

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-0.5, 0.3333333333333333)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.25, c=0.0, expected=-0.0009765625),
        FormulaTestCase.value(params={}, x=-0.25, c=0.25, expected=-0.02020748979611757),
        FormulaTestCase.interval_bounds(params={}, expected=(-0.5, 0.3333333333333333)),
    )
