"""This module holds a formula of Süli, Mayers (2003).

The formula comes from the row with the key ``Exercise 1.2`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class SuliMayers2003Exercise12(Formula):
    """This formula comes from Süli, Mayers (2003).

    The survey writes the source's function as ``x = g(x)``, with ``g(x) = -x*sin(1/x)^2`` for ``0 < x <= 1`` and ``g(0)
    = 0``, with the parameters ``k`` integer; the formula's interval is ``[0, 1]``.

    Fixed point 0, neither stable nor unstable; starts ``x0 = 1/(k*pi)`` and ``x0 = 2/((2*k + 1)*pi)``.

    The formula is the difference form ``x - g(x)`` of the fixed-point equation ``x = g(x)``; ``k``, which the starting
    points use, is not a parameter of the function.
    """

    number = (1, 4, 2, 6)
    name = "Exercise 1.2"
    params = ()
    location_in_publication = "Exercise 1.2"
    presentation = FormulaPresentation(
        definitions=(
            (r"\tmp{u}", r"\x - \c"),
            (r"\fn{g}(\x)", r"-\x \sin^2 \frac{1}{\x}"),
        ),
        expression=(
            r"\begin{cases} "
            r"0 & \text{if } \tmp{u} = 0 \\ "
            r"\tmp{u} - \fn{g}(\tmp{u}) & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[0, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        # the formula is the difference form x - g(x) of the fixed-point equation x = g(x), with g(0) = 0
        if x == 0.0:
            return 0.0
        else:
            return x + x * math.sin(1.0 / x) ** 2

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.3108948445423537),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=0.0916734515413067),
        FormulaTestCase.value(params={}, x=0.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
