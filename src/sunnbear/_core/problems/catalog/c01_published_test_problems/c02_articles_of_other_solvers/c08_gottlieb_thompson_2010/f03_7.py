"""This module holds a formula of Gottlieb, Thompson (2010).

The formula comes from the row with the key ``7`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class GottliebThompson20107(Formula):
    """This formula comes from Gottlieb, Thompson (2010).

    The survey writes the source's function as ``1/x - 1``; the formula's interval is ``[0.5, 2.0]``.

    Table 2's root `1.0000000000`.
    """

    number = (1, 2, 8, 3)
    name = "7"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Gottlieb, R. G., Thompson, B. F. (2010). Bisected direct quadratic regula falsi. Applied "
            "Mathematical Sciences 4(15), 709–718. No DOI; the publisher's copy: "
            "http://www.m-hikari.com/ams/ams-2010/ams-13-16-2010/gottliebAMS13-16-2010.pdf."
        ),
        location="7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.5 * c
        return 1 / x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.95, c=0.0, expected=0.052631578947368474),
        FormulaTestCase.value(params={}, x=0.95, c=0.25, expected=0.7391304347826089),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 2.0)),
    )
