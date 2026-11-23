"""This module holds a formula of roots-fortran (2025).

The formula comes from the row with the key ``138–139`` in the survey of published test problems.
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


class RootsFortran2025Case138(Formula):
    """This formula comes from roots-fortran (2025).

    The survey writes the source's function as ``abs(x - 2.0/3.0)^0.5 - 0.1`` (x <= 2.0/3.0); ``-abs(x - 2.0/3.0)^0.5 -
    0.1`` (otherwise); the formula's intervals are ``[-10, 10]`` (138), ``[-10000, 10]`` (139).

    Stage §3.7
    """

    number = (1, 3, 3, 38)
    name = "Case 138"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, cases 138 and 139"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"|\tmp{u} - 2/3|^{0.5} - 0.1 & \text{if } \tmp{u} \le 2/3 \\ "
            r"-|\tmp{u} - 2/3|^{0.5} - 0.1 & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            r"The signed square root of $2/3 - \x$, lowered by 0.1, with its root 0.01 below $\x = 2/3$, where the "
            r"slope is infinite."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if x <= 2.0 / 3.0:
            return abs(x - 2.0 / 3.0) ** 0.5 - 0.1
        else:
            return -(abs(x - 2.0 / 3.0) ** 0.5) - 0.1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-10.0, 10.0, 20.0), (-10000.0, 10.0, 10000.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.0, expected=2.060246899469287
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=-4.0, c=0.25, expected=3.009126351029605
        ),
        FormulaTestCase.value(
            params={"a": -10000.0, "b": 10.0, "c_scale": 10000.0}, x=-6997.0, c=0.0, expected=83.55205715741046
        ),
        FormulaTestCase.value(
            params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, x=5.0, c=0.0, expected=-2.1816659994661327
        ),
        FormulaTestCase.interval_bounds(params={"a": -10.0, "b": 10.0, "c_scale": 20.0}, expected=(-10.0, 10.0)),
        FormulaTestCase.interval_bounds(
            params={"a": -10000.0, "b": 10.0, "c_scale": 10000.0}, expected=(-10000.0, 10.0)
        ),
    )
