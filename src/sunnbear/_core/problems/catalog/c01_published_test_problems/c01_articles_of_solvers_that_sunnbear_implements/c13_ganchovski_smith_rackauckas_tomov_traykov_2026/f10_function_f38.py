"""This module holds a formula of Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

The formula comes from the rows with the keys ``f38`` and ``f39`` in the survey of published test problems.
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


class GanchovskiSmithRackauckasTomovTraykov2026FunctionF38(Formula):
    """This formula comes from Ganchovski, Smith, Rackauckas, Tomov, Traykov (2026).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``if(x <= 1/3; -d; 1 - d)``:

    - f38, with ``d = 0.5``: ``if(x <= 1/3; -0.5; 0.5)``; the formula's interval is ``[-11, 9]``
    - f39, with ``d = 10^-3``: ``if(x <= 1/3; -10^-3; 1 - 10^-3)``; the formula's interval is ``[-11, 9]``
    """

    number = (1, 1, 13, 10)
    name = "Function f38"
    params = (FormulaParam("d", latex_symbol="d"),)
    location_in_publication = "Table 2, f38 and f39"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=(
            r"\begin{cases} - \param{d} & \text{for}\: \tmp{u} \leq \frac{1}{3} \\1 - \param{d} & "
            r"\text{otherwise} \end{cases}"
        ),
        interval="[-11, 9]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        if x <= 1 / 3:
            return -d
        else:
            return 1 - d

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-11.0, 9.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("d",), rows=((0.5,), (0.001,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"d": 0.5}, x=-5.0, c=0.0, expected=-0.5),
        FormulaTestCase.value(params={"d": 0.5}, x=-5.0, c=0.25, expected=-0.5),
        FormulaTestCase.value(params={"d": 0.5}, x=9.0, c=0.0, expected=0.5),
        FormulaTestCase.value(params={"d": 0.001}, x=-5.0, c=0.0, expected=-0.001),
        FormulaTestCase.interval_bounds(params={"d": 0.5}, expected=(-11.0, 9.0)),
    )
