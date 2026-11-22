"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``155–157`` in the survey of published test problems.
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


class RootsFortran2025155157(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(x^2 - x - 6.0)*(x^2 - 3.0*x + 2.0)``; the formula's intervals are
    ``[0, 1.9] (155), [1.001, 2.001] (156), [2.5, 10] (157)``.

    a different root in each bracket
    """

    number = (1, 3, 3, 44)
    name = "155–157"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, case 155–157"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\tmp{u}^{2} - \tmp{u} - 6.0\right) \left(\tmp{u}^{2} - 3.0 \tmp{u} + 2.0\right)",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x**2 - x - 6.0) * (x**2 - 3.0 * x + 2.0)

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.9, 1.9), (1.001, 2.001, 1.0), (2.5, 10.0, 7.5)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.9, "c_scale": 1.9}, x=0.57, c=0.0, expected=-3.8401119900000005),
        FormulaTestCase.value(params={"a": 0.0, "b": 1.9, "c_scale": 1.9}, x=0.57, c=0.25, expected=-10.492373049375),
        FormulaTestCase.value(
            params={"a": 1.001, "b": 2.001, "c_scale": 1.0}, x=1.301, c=0.0, expected=1.1800015412009999
        ),
        FormulaTestCase.value(params={"a": 2.5, "b": 10.0, "c_scale": 7.5}, x=4.75, c=0.0, expected=121.81640625),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.9, "c_scale": 1.9}, expected=(0.0, 1.9)),
        FormulaTestCase.interval_bounds(params={"a": 1.001, "b": 2.001, "c_scale": 1.0}, expected=(1.001, 2.001)),
        FormulaTestCase.interval_bounds(params={"a": 2.5, "b": 10.0, "c_scale": 7.5}, expected=(2.5, 10.0)),
    )
