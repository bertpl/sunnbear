"""This module holds a formula of Naghipoor, Ahmadian, Soheili (2008).

The formula comes from the row with the key ``T1.6`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class NaghipoorAhmadianSoheili2008T16(Formula):
    """This formula comes from Naghipoor, Ahmadian, Soheili (2008).

    The survey writes the source's function as ``1/x - 1``; the formula's interval is ``[0.5, 1.5]``.

    Table 1 prints the final iterate `x_n` as `1.0000000000`.
    """

    number = (1, 2, 7, 5)
    name = "T1.6"
    params = ()
    source = FormulaSource(
        reference=(
            "Naghipoor, J., Ahmadian, S. A., Soheili, A. R. (2008). An Improved Regula Falsi Method for"
            " Finding Simple Zeros of Nonlinear Equations. Applied Mathematical Sciences 2(8), 381–386."
            " No DOI; the publisher's copy: "
            "https://www.m-hikari.com/ams/ams-password-2008/ams-password5-8-2008/soheiliAMS5-8-2008.pdf."
        ),
        location="Table 1, equation 6",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\frac{1}{\tmp{u}} - 1",
        interval="[0.5, 1.5]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 1 / x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.5, 1.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.8, c=0.0, expected=0.24999999999999994),
        FormulaTestCase.value(params={}, x=0.8, c=0.25, expected=0.818181818181818),
        FormulaTestCase.interval_bounds(params={}, expected=(0.5, 1.5)),
    )
