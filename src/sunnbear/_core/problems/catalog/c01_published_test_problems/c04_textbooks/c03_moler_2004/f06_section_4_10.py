"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§4.7, §4.10`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Moler2004Section410(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``1/((x - 0.3)^2 + 0.01) + 1/((x - 0.9)^2 + 0.04) - 6``; the formula's
    interval is `[-1, 2]` (Figure 4.8).

    MATLAB's demo function `humps`, which §4.10 says illustrates graphics, quadrature and zero-finding routines; §4.7
    names the handle `@humps` as an example of syntax. The chapter uses it only for minimization: `fmintx` minimizes
    `-humps(x)` on `[-1, 2]` (§4.10, Figure 4.8; Ex. 4.17).
    """

    number = (1, 4, 3, 6)
    name = "Section 4.10"
    params = ()
    location_in_publication = "§4.7, §4.10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\frac{1}{\left(\tmp{u} - 0.3\right)^{2} + 0.01} + \frac{1}{\left(\tmp{u} - 0.9\right)^{2} " r"+ 0.04} - 6"
        ),
        interval="[-1, 2]",
        summary=(
            "A function, negative at both bounds, with 2 steep peaks and 1 simple root on each side of the peaks, "
            'referred to in the source as "humps".'
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return 1 / ((x - 0.3) ** 2 + 0.01) + 1 / ((x - 0.9) ** 2 + 0.04) - 6

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.1, c=0.0, expected=0.843891402714932),
        FormulaTestCase.value(params={}, x=-0.1, c=0.75, expected=-4.92721024774247),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 2.0)),
    )
