"""This module holds a formula of roots-fortran (2025).

The formula comes from the rows with the keys ``69`` and ``105`` in the survey of published test problems.
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


class RootsFortran2025Case69(Formula):
    """This formula comes from roots-fortran (2025).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``x^2 - k``:

    - 69, with ``k = 1.0``: ``x^2 - 1.0``; the formula's interval is ``[0.1001, 10.0001]``
    - 105, with ``k = 10.0``: ``x^2 - 10.0``; the formula's interval is ``[3, 7]``

    105: Badr `P3`
    """

    number = (1, 3, 3, 21)
    name = "Case 69"
    params = (
        FormulaParam("k", latex_symbol="k"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "root_tests.f90, cases 69 and 105"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{2} - \param{k}",
        interval=r"[\param{a}, \param{b}]",
        summary="A parabola on 2 intervals, each with 1 root close to its lower bound.",
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, k: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**2 - k

    def interval_bounds(self, k: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("k", "a", "b", "c_scale"),
                rows=((1.0, 0.1001, 10.0001, 9.9), (10.0, 3.0, 7.0, 4.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"k": 1.0, "a": 0.1001, "b": 10.0001, "c_scale": 9.9}, x=3.0701, c=0.0, expected=8.42551401
        ),
        FormulaTestCase.value(
            params={"k": 1.0, "a": 0.1001, "b": 10.0001, "c_scale": 9.9}, x=3.0701, c=0.25, expected=-0.64585599
        ),
        FormulaTestCase.value(
            params={"k": 10.0, "a": 3.0, "b": 7.0, "c_scale": 4.0}, x=4.2, c=0.0, expected=7.6400000000000015
        ),
        FormulaTestCase.interval_bounds(
            params={"k": 1.0, "a": 0.1001, "b": 10.0001, "c_scale": 9.9}, expected=(0.1001, 10.0001)
        ),
        FormulaTestCase.interval_bounds(params={"k": 10.0, "a": 3.0, "b": 7.0, "c_scale": 4.0}, expected=(3.0, 7.0)),
    )
