"""This module holds a formula of Oliveira, Takahashi (2021).

The formula comes from the row with the key ``1.8`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import real_root, sign


class OliveiraTakahashi202118(Formula):
    """This formula comes from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``1/3 + sign(x)*abs(x)^(1/3) + x^3``; the formula's interval is ``[-1,
    1]``.
    """

    number = (1, 1, 9, 7)
    name = "1.8"
    params = ()
    location_in_publication = "Table 1, well-behaved function 8"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\frac{1}{3} + \operatorname{sign}{\left(\tmp{u} \right)} \sqrt[3]{\left|{\tmp{u}}\right|} "
            r"+ \tmp{u}^{3}"
        ),
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return 1 / 3 + sign(x) * real_root(abs(x), 3) + x**3

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.467472966394744),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-1.3611560512722964),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
