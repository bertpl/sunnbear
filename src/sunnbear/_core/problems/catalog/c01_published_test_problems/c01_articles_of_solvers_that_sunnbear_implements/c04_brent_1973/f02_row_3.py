"""This module holds a formula of Brent (1973).

The formula comes from the row with the key ``T4.1 r3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Brent1973Row3(Formula):
    """This formula comes from Brent (1973).

    The survey writes the source's function as ``x^19``; the formula's interval is `[-1.0, +4.0]` with the absolute
    tolerance `t = 1E-20` of procedure `zero2`.
    """

    number = (1, 1, 4, 2)
    name = "Row 3"
    params = ()
    location_in_publication = "Table 4.1, row 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 5 \c"),),
        expression=r"\tmp{u}^{19}",
        interval="[-1, 4]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 5.0 * c
        return x**19

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.5, c=0.0, expected=1.9073486328125e-06),
        FormulaTestCase.value(params={}, x=0.5, c=0.25, expected=-0.004228282585245324),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 4.0)),
    )
