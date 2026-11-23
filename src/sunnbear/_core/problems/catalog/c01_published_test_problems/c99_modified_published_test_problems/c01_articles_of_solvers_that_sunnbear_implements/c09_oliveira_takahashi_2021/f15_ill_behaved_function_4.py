"""This module holds formula f1.99.1.9.15, the modified version of the published formula f1.1.9.15.

A change of formula f1.1.9.15 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)
from sunnbear._core.utils.math_functions import sign


class ModifiedOliveiraTakahashi2021IllBehavedFunction4(Formula):
    """This formula is the modified version of formula f1.1.9.15, from Oliveira, Takahashi (2021).

    The survey writes the source's function as ``sign(3*x + 1)*(1 - sqrt(1 - (3*x + 1)^2/9^2))``; the published interval
    is ``[-1, 1]``.

    The formula computes the published function in the equivalent form
    ``sign(3*x + 1) * ((3*x + 1)**2/9**2) / (1 + sqrt(1 - (3*x + 1)**2/9**2))``, on the published interval, and ``c``
    shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, ``sqrt(1 - (3*x + 1)**2/9**2)`` rounds to 1, and its subtraction from 1 cancels, so that f is exactly
    0 at many x-values within about 2e-8 of the root; the equivalent form has no subtraction that cancels.
    """

    number = (1, 99, 1, 9, 15)
    name = "Ill-behaved function 4"
    params = ()
    location_in_publication = "Table 1, ill-behaved function 4"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=(
            r"\operatorname{sign}{\left(3 \tmp{u} + 1 \right)} \frac{\left(3 \tmp{u} + 1\right)^{2} / "
            r"9^{2}}{1 + \sqrt{1 - \left(3 \tmp{u} + 1\right)^{2} / 9^{2}}}"
        ),
        interval="[-1, 1]",
        summary=(
            "A pair of elliptical arcs that cross 0 at the root with a slope of 0, referred to in the source as "
            '"Circles".'
        ),
        notes=(
            (
                r"The expression equals the published function, $$\operatorname{sign}{\left(3 \tmp{u} + 1 "
                r"\right)} \left(1 - \sqrt{1 - \frac{\left(3 \tmp{u} + 1\right)^{2}}{9^{2}}}\right),$$ "
                "without the cancellation that makes the published function exactly 0 at many x-values "
                "next to the root."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, in an equivalent form without cancellation.

        The form is ``sign(3*y + 1) * ((3*y + 1)**2/9**2) / (1 + sqrt(1 - (3*y + 1)**2/9**2))``. Category 1 states the
        rule for ``c_scale``.
        """
        x = x - 2.0 * c
        return sign(3 * x + 1) * ((3 * x + 1) ** 2 / 9**2) / (1 + math.sqrt(1 - (3 * x + 1) ** 2 / 9**2))

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.018001533782093432),
    )
