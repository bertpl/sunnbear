"""This module holds a formula of Naghipoor, Ahmadian, Soheili (2008).

The formula comes from the row with the key ``T1.2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class NaghipoorAhmadianSoheili2008T12(Formula):
    """This formula comes from Naghipoor, Ahmadian, Soheili (2008).

    The survey writes the source's function as ``11*x^11 - 1``; the formula's interval is ``[0.1, 0.9]``.

    Table 1 prints the final iterate `x_n` as `0.8041330975`.
    """

    number = (1, 2, 7, 2)
    name = "T1.2"
    params = ()
    location_in_publication = "Table 1, equation 2"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.8 \c"),),
        expression=r"11 \tmp{u}^{11} - 1",
        interval="[0.1, 0.9]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.8 * c
        return 11 * x**11 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.1, 0.9)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.34, c=0.0, expected=-0.9999227922719982),
        FormulaTestCase.value(params={}, x=0.34, c=0.25, expected=-0.9999999955454784),
        FormulaTestCase.interval_bounds(params={}, expected=(0.1, 0.9)),
    )
