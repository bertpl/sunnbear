"""This module holds a formula of Gao (2026).

The formula comes from the row with the key ``T2.2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Gao2026T22(Formula):
    """This formula comes from Gao (2026).

    The survey writes the source's function as ``x^7``; the formula's interval is ``[-3, 5]``.

    Also named in Section 3's opening paragraphs.
    """

    number = (1, 1, 14, 4)
    name = "T2.2"
    params = ()
    source = FormulaSource(
        reference=(
            "Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied "
            "Mathematics Letters 178, 109928. https://doi.org/10.1016/j.aml.2026.109928."
        ),
        location="T2.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 8.0 * c
        return x**7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-3.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.6, c=0.0, expected=-0.027993599999999993),
        FormulaTestCase.value(params={}, x=-0.6, c=0.25, expected=-803.1810176000002),
        FormulaTestCase.interval_bounds(params={}, expected=(-3.0, 5.0)),
    )
