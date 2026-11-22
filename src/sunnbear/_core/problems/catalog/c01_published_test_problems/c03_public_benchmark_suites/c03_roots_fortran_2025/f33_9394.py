"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``93–94`` in the survey of published test problems.
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


class RootsFortran20259394(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(x - 10.0)*x + 23.0 - x^0.4``; the formula's intervals are ``[0, 6]
    (93), [6, 8] (94)``.

    a different root in each bracket
    """

    number = (1, 3, 3, 33)
    name = "93–94"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, case 93–94"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\tmp{u} - 10.0\right) \tmp{u} + 23.0 - \tmp{u}^{0.4}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x - 10.0) * x + 23.0 - x**0.4

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"), rows=((0.0, 6.0, 6.0), (6.0, 8.0, 2.0)), summary="The published intervals."
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 6.0, "c_scale": 6.0}, x=1.8, c=0.0, expected=6.97494618097175),
        FormulaTestCase.value(params={"a": 0.0, "b": 6.0, "c_scale": 6.0}, x=1.8, c=0.25, expected=19.472199149432587),
        FormulaTestCase.value(params={"a": 6.0, "b": 8.0, "c_scale": 2.0}, x=6.6, c=0.0, expected=-1.5672453070053973),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 6.0, "c_scale": 6.0}, expected=(0.0, 6.0)),
        FormulaTestCase.interval_bounds(params={"a": 6.0, "b": 8.0, "c_scale": 2.0}, expected=(6.0, 8.0)),
    )
