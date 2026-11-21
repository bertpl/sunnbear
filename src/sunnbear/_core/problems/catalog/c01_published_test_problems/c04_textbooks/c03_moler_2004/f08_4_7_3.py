"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§4.7#3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)
from sunnbear._core.utils.math_functions import bessel_j0


class Moler2004473(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``J0(x) - y``, with the parameters ``y = 0.5``; the formula's interval is
    ``[0, 2]``.

    §4.7 states the equation `J0(xi) = 0.5` and passes `F = @(x,y) besselj(0,x)-y`, or `B = @(x,n,y) besselj(n,x)-y`
    with `n = 0`, to `fzerotx` with `y = 0.5`. Result `xi = 1.5211`; Figure 4.2, which plots `J0(x)` on `[0, 10*pi]`,
    marks the point `(xi, J0(xi))`.
    """

    number = (1, 4, 3, 8)
    name = "§4.7#3"
    params = (FormulaParam("y", latex_symbol="y"),)
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="§4.7, function 3",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"J_{0}\left(\tmp{u}\right) - \param{y}",
        interval="[0, 2]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, y: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return bessel_j0(x) - y

    def interval_bounds(self, y: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("y",), rows=((0.5,),), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"y": 0.5}, x=0.6, c=0.0, expected=0.41200486349721077),
        FormulaTestCase.value(params={"y": 0.5}, x=0.6, c=0.25, expected=0.49750156206604),
        FormulaTestCase.interval_bounds(params={"y": 0.5}, expected=(0.0, 2.0)),
    )
