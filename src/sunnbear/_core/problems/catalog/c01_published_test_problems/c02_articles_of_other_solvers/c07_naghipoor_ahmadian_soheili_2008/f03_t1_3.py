"""This module holds a formula of Naghipoor, Ahmadian, Soheili (2008).

The formula comes from the row with the key ``T1.3`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class NaghipoorAhmadianSoheili2008T13(Formula):
    """This formula comes from Naghipoor, Ahmadian, Soheili (2008).

    The survey writes the source's function as ``exp(x^2 + 7*x - 30) - 1``; the formula's interval is ``[2.8, 3.1]``.

    Table 1 prints the final iterate `x_n` as `3.0000000000`.
    """

    number = (1, 2, 7, 3)
    name = "T1.3"
    params = ()
    source = FormulaSource(
        reference=(
            "Naghipoor, J., Ahmadian, S. A., Soheili, A. R. (2008). An Improved Regula Falsi Method for"
            " Finding Simple Zeros of Nonlinear Equations. Applied Mathematical Sciences 2(8), 381–386."
            " No DOI; the publisher's copy: "
            "https://www.m-hikari.com/ams/ams-password-2008/ams-password5-8-2008/soheiliAMS5-8-2008.pdf."
        ),
        location="T1.3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.3 * c
        return math.exp(x**2 + 7 * x - 30) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.8, 3.1)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.89, c=0.0, expected=-0.7577778503147906),
        FormulaTestCase.value(params={}, x=2.89, c=0.25, expected=-0.9065916932186274),
        FormulaTestCase.interval_bounds(params={}, expected=(2.8, 3.1)),
    )
