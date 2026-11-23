"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§1.7`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
)


class Moler2004Section17(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``x^7 - 7*x^6 + 21*x^5 - 35*x^4 + 35*x^3 - 21*x^2 + 7*x - 1``; the
    formula's interval is ``[0.988, 1.012]``.

    The expanded form of `(x - 1)^7`, which the book says was made with the Symbolic Toolbox. §1.7 plots it at `x =
    0.988:.0001:1.012` (Figure 1.9, "Is this a polynomial?") to show roundoff error: the plot is not smooth, with values
    of order `10^-14`, because of subtractive cancellation; evaluated as `(x-1).^7`, the plot is smooth. No root is
    sought.
    """

    number = (1, 4, 3, 2)
    name = "Section 1.7"
    params = ()
    location_in_publication = "§1.7"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 0.024 \c"),),
        expression=(
            r"\tmp{u}^{7} - 7 \tmp{u}^{6} + 21 \tmp{u}^{5} - 35 \tmp{u}^{4} + 35 \tmp{u}^{3} - 21 "
            r"\tmp{u}^{2} + 7 \tmp{u} - 1"
        ),
        interval="[0.988, 1.012]",
        summary=(
            r"$(\x - 1)^7$ written out as a polynomial, whose rounding errors decide the polynomial's sign over about "
            r"85% of the interval."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 0.024 * c
        return x**7 - 7 * x**6 + 21 * x**5 - 35 * x**4 + 35 * x**3 - 21 * x**2 + 7 * x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.988, 1.012)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.value(params={}, x=0.9952, c=0.0, expected=-5.870683422720226e-17, atol=4e-13),
        FormulaTestCase.value(params={}, x=0.9952, c=0.25, expected=-1.7138242687795553e-14, atol=4e-13),
        FormulaTestCase.interval_bounds(params={}, expected=(0.988, 1.012)),
    )
