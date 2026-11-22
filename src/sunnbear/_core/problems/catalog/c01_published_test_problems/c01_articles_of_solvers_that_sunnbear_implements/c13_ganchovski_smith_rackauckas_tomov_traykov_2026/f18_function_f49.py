"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the row with the key ``f49`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import real_root


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF49(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The survey writes the source's function as ``if(x <= 0; -x^3 - x - 1; x^(1/3) - x - 1)``; the formula's interval is
    ``[-1, 1]``.

    The formula follows the article and `Test Functions.pdf`, which print `x^(1/3)`; the plot in `Test Functions.pdf`
    shows the cube-root branch. The C# code writes the exponent `1/3` as an integer division, which is 0, so it computes
    `x^0 - x - 1` for `x > 0`, as does sunnbear's test transcription in
    `tests/solvers/paper_problems/ganchovski_et_al.py`.
    """

    number = (1, 1, 13, 18)
    name = "Function f49"
    params = ()
    location_in_publication = "Table 2, f49"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\begin{cases} - \tmp{u}^{3} - \tmp{u} - 1 & \text{for}\: \tmp{u} \leq 0 "
            r"\\\sqrt[3]{\tmp{u}} - \tmp{u} - 1 & \text{otherwise} \end{cases}"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        if x <= 0:
            return -(x**3) - x - 1
        else:
            return real_root(x, 3) - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.5359999999999999),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=0.6290000000000001),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=-1.0),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
