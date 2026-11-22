"""This module holds a formula of roots-fortran (2025).

The formula comes from the rows with the keys ``71–72`` and ``132`` in the survey of published test problems.
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


class RootsFortran20257172(Formula):
    """This formula comes from roots-fortran (2025).

    The source prints 1 function in 2 rows, each on its own interval:

    - 71–72: ``x``; the formula's intervals are ``[-2.0001, 1.0001] (71), [-0.0001, 1.0001] (72)``
    - 132: ``x``; the formula's interval is ``[-1000, 1]``

    71–72: the comment on case 72 says "root very close to a"
    """

    number = (1, 3, 3, 23)
    name = "71–72"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, cases 71–72 and 132"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}",
        interval=r"[\param{a}, \param{b}]",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        return x - c_scale * c

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((-2.0001, 1.0001, 3.0), (-0.0001, 1.0001, 1.0), (-1000.0, 1.0, 1000.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": -2.0001, "b": 1.0001, "c_scale": 3.0}, x=-1.10004, c=0.0, expected=-1.10004),
        FormulaTestCase.value(
            params={"a": -2.0001, "b": 1.0001, "c_scale": 3.0}, x=-1.10004, c=0.25, expected=-1.85004
        ),
        FormulaTestCase.value(params={"a": -0.0001, "b": 1.0001, "c_scale": 1.0}, x=0.29996, c=0.0, expected=0.29996),
        FormulaTestCase.value(params={"a": -1000.0, "b": 1.0, "c_scale": 1000.0}, x=-699.7, c=0.0, expected=-699.7),
        FormulaTestCase.interval_bounds(params={"a": -2.0001, "b": 1.0001, "c_scale": 3.0}, expected=(-2.0001, 1.0001)),
        FormulaTestCase.interval_bounds(params={"a": -0.0001, "b": 1.0001, "c_scale": 1.0}, expected=(-0.0001, 1.0001)),
        FormulaTestCase.interval_bounds(params={"a": -1000.0, "b": 1.0, "c_scale": 1000.0}, expected=(-1000.0, 1.0)),
    )
