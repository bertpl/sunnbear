"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``84–85`` in the survey of published test problems.
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


class RootsFortran2025Case84(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``(((x*x - 6.0)*x - 8.0)*x - 3.0)*x^4 - 1.0``; the formula's intervals
    are ``[-5, 0] (84), [0, 5] (85)``.

    a different root in each bracket
    """

    number = (1, 3, 3, 29)
    name = "Case 84"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, case 84–85"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\left(\left(\left(\tmp{u} \tmp{u} - 6.0\right) \tmp{u} - 8.0\right) \tmp{u} - 3.0\right) "
            r"\tmp{u}^{4} - 1.0"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"$\tmp{u}^4 (\tmp{u} + 1)^3 (\tmp{u} - 3) - 1$ multiplied out, with 1 root on each interval, flat around "
            r"$\x = 5 \c$ and steep at the intervals' outer bounds."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (((x * x - 6.0) * x - 8.0) * x - 3.0) * x**4 - 1.0

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-5.0, 0.0, 5.0), (0.0, 5.0, 5.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -5.0, "b": 0.0, "c_scale": 5.0}, x=-3.5, c=0.0, expected=15239.72265625),
        FormulaTestCase.value(params={"a": -5.0, "b": 0.0, "c_scale": 5.0}, x=-3.5, c=0.25, expected=208050.0654449463),
        FormulaTestCase.value(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, x=1.5, c=0.0, expected=-119.65234375),
        FormulaTestCase.interval_bounds(params={"a": -5.0, "b": 0.0, "c_scale": 5.0}, expected=(-5.0, 0.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 5.0, "c_scale": 5.0}, expected=(0.0, 5.0)),
    )
