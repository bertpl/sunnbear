"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.1#2`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class Moler2004Ex412(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``x^3 - 0.001``; the formula's interval is ``[-1, 1]``.
    """

    number = (1, 4, 3, 10)
    name = "Ex. 4.1#2"
    params = ()
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="Exercise 4.1, function 2",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 2 \c"),),
        expression=r"\tmp{u}^{3} - 0.001",
        interval="[-1, 1]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 2.0 * c
        return x**3 - 0.001

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-0.4, c=0.0, expected=-0.06500000000000002),
        FormulaTestCase.value(params={}, x=-0.4, c=0.25, expected=-0.7300000000000001),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 1.0)),
    )
