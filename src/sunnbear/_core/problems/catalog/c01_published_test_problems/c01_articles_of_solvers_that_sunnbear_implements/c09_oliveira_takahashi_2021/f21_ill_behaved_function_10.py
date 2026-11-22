"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``2.10`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class OliveiraTakahashi2021IllBehavedFunction10(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``(x > -1)*(1 + sin(1/(x + 1))) - 1``; the formula's interval is ``[-1,
    1]``.

    The authors' MATLAB code and sunnbear's test transcription in `tests/solvers/paper_problems/oliveira_takahashi.py`
    write the same function as `sin(1/(x + 1))` for `x > -1` and `-1` elsewhere. At `x = -1`, where the printed product
    holds `sin(1/0)`, they return `-1`, and so does the formula, which evaluates `sin(1/(x + 1))` only for `x > -1`.
    """

    number = (1, 1, 9, 21)
    name = "Ill-behaved function 10"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 10"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\begin{cases} 1 + \sin{\left(\frac{1}{\tmp{u} + 1} \right)} & \text{for}\: \tmp{u} > -1 "
            r"\\0 & \text{otherwise} \end{cases} - 1"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return ((1 + math.sin(1 / (x + 1))) if (x) > (-1) else 0.0) - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=0.9954079577517649),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.5440211108893717),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
