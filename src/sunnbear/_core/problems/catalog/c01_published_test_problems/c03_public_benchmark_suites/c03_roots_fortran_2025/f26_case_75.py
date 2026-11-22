"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``75–78`` in the survey of published test problems.
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


class RootsFortran2025Case75(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``((x*x - 27.0)*x - 54.0)*x - 10.0``; the formula's intervals are ``[-5,
    -3] (75), [-3, -2] (76), [-2, 0] (77), [0, 9] (78)``.

    a different root in each bracket
    """

    number = (1, 3, 3, 26)
    name = "Case 75"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, case 75–78"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\left(\left(\tmp{u} \tmp{u} - 27.0\right) \tmp{u} - 54.0\right) \tmp{u} - 10.0",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return ((x * x - 27.0) * x - 54.0) * x - 10.0

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-5.0, -3.0, 2.0), (-3.0, -2.0, 1.0), (-2.0, 0.0, 2.0), (0.0, 9.0, 9.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -5.0, "b": -3.0, "c_scale": 2.0}, x=-4.4, c=0.0, expected=79.68960000000006),
        FormulaTestCase.value(
            params={"a": -5.0, "b": -3.0, "c_scale": 2.0}, x=-4.4, c=0.25, expected=182.8101000000001
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": -2.0, "c_scale": 1.0}, x=-2.7, c=0.0, expected=-7.885900000000002
        ),
        FormulaTestCase.value(params={"a": -2.0, "b": 0.0, "c_scale": 2.0}, x=-1.4, c=0.0, expected=16.5216),
        FormulaTestCase.value(params={"a": 0.0, "b": 9.0, "c_scale": 9.0}, x=2.7, c=0.0, expected=-299.4859),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": -3.0, "c_scale": 2.0}, expected=(-5.0, -3.0)),
        FormulaTestCase.interval_bounds(params={"a": -3.0, "b": -2.0, "c_scale": 1.0}, expected=(-3.0, -2.0)),
        FormulaTestCase.interval_bounds(params={"a": -2.0, "b": 0.0, "c_scale": 2.0}, expected=(-2.0, 0.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 9.0, "c_scale": 9.0}, expected=(0.0, 9.0)),
    )
