"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``21`` in the survey of published test problems.
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


class RootsFortran2025Case21(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``x^2 - (1.0 - x)^n``, with the parameters ``n = 2, 5, 10, 15, 20``; the
    formula's interval is ``[0, 1.01]``.
    """

    number = (1, 3, 3, 3)
    name = "Case 21"
    params = (FormulaParam("n", latex_symbol="n"),)
    location_in_publication = "root_tests.f90, case 21"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 1.01 \c"),),
        expression=r"\tmp{u}^{2} - \left(1.0 - \tmp{u}\right)^{\param{n}}",
        interval="[0, 1.01]",
        summary=(
            r"A function that is a line at $\param{n} = 2$ and, as $\param{n}$ grows, steeper at the lower bound, with "
            r"its 1 root closer to it."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.01 * c
        return x**2 - (1.0 - x) ** n

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.01)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("n",),
                rows=((2.0,), (5.0,), (10.0,), (15.0,), (20.0,)),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.303, c=0.0, expected=-0.394),
        FormulaTestCase.value(params={"n": 2.0}, x=0.303, c=0.25, expected=-0.899),
        FormulaTestCase.value(params={"n": 5.0}, x=0.303, c=0.0, expected=-0.07269023798325701),
        FormulaTestCase.value(params={"n": 10.0}, x=0.303, c=0.0, expected=0.06474900070292777),
        FormulaTestCase.value(params={"n": 15.0}, x=0.303, c=0.0, expected=0.08735765073580415),
        FormulaTestCase.value(params={"n": 20.0}, x=0.303, c=0.0, expected=0.09107675643804244),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(0.0, 1.01)),
    )
