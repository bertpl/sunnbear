"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``2.3-1, 2.3-3`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaSource,
    FormulaTestCase,
    ParamRecipe,
)


class BurdenFairesBurden2016231(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^2 - 6``; the formula's interval is `[2, 3]` (false position, 2.3-3).

    Newton from `p0 = 1` to `p2` (2.3-1); secant and false position from `p0 = 3, p1 = 2` to `p3`, and which is closer
    to `sqrt(6)` (2.3-3).
    """

    number = (1, 4, 7, 29)
    name = "2.3-1"
    params = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="Exercises 2.3-1, 2.3-3",
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=r"\tmp{u}^{2} - 6",
        interval="[2, 3]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - 6

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (2.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=2.3, c=0.0, expected=-0.7100000000000009),
        FormulaTestCase.value(params={}, x=2.3, c=0.25, expected=-1.7975000000000008),
        FormulaTestCase.interval_bounds(params={}, expected=(2.0, 3.0)),
    )
