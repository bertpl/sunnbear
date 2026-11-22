"""This module holds a formula of Bus, Dekker (1975).

The formula comes from the row with the key ``III`` in the survey of published test problems.
"""

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class BusDekker1975Iii(Formula):
    """This formula comes from Bus, Dekker (1975).

    The survey writes the source's function as ``x^n``, with the parameters ``n = 3, 5, 7, 9, 19, 25``; the formula's
    interval is ``[-1, 10]``.

    Group III: a zero of multiplicity `n` at 0.
    """

    number = (1, 2, 1, 5)
    name = "III"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "Group III"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 11 \c"),),
        expression=r"\tmp{u}^{\param{n}}",
        interval="[-1, 10]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 11.0 * c
        return x**n

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=((3.0,), (5.0,), (7.0,), (9.0,), (19.0,), (25.0,)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 3.0}, x=2.3, c=0.0, expected=12.166999999999998),
        FormulaTestCase.value(params={"n": 3.0}, x=2.3, c=0.25, expected=-0.09112500000000011),
        FormulaTestCase.value(params={"n": 5.0}, x=2.3, c=0.0, expected=64.36342999999998),
        FormulaTestCase.value(params={"n": 7.0}, x=2.3, c=0.0, expected=340.48254469999983),
        FormulaTestCase.value(params={"n": 9.0}, x=2.3, c=0.0, expected=1801.1526614629988),
        FormulaTestCase.value(params={"n": 19.0}, x=2.3, c=0.0, expected=7461547.09275906),
        FormulaTestCase.value(params={"n": 25.0}, x=2.3, c=0.0, expected=1104576757.1919525),
        FormulaTestCase.interval_bounds(params={"n": 3.0}, expected=(-1.0, 10.0)),
    )
