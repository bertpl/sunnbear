"""This module holds a formula of Sabharwal (2019).

The formula comes from the rows with the keys ``T2.1``, ``T2.2`` and ``T2.3`` in the survey of published test problems.
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


class Sabharwal2019Function1(Formula):
    """This formula comes from Sabharwal (2019).

    The source prints 3 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 3 functions become 1 function, ``x^2 - k``:

    - T2.1, with ``k = 3``: ``x^2 - 3``; the formula's interval is ``[1, 2]``
    - T2.2, with ``k = 5``: ``x^2 - 5``; the formula's interval is ``[2, 7]``
    - T2.3, with ``k = 10``: ``x^2 - 10``; the formula's interval is ``[3, 4]``
    """

    number = (1, 2, 13, 5)
    name = "Function 1"
    params = (
        FormulaParam("k", latex_symbol="k"),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Table 2, functions 1, 2 and 3"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{2} - \param{k}",
        interval=r"[\param{a}, \param{b}]",
        summary="A parabola with 1 simple root on each of the 3 intervals, close to the lower bound on the widest one.",
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
                rows=((3.0, 1.0, 2.0, 1.0), (5.0, 2.0, 7.0, 5.0), (10.0, 3.0, 4.0, 1.0)),
                summary="The published parameter values and intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"k": 3.0, "a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.0, expected=-1.3099999999999998
        ),
        FormulaTestCase.value(params={"k": 3.0, "a": 1.0, "b": 2.0, "c_scale": 1.0}, x=1.3, c=0.25, expected=-1.8975),
        FormulaTestCase.value(params={"k": 5.0, "a": 2.0, "b": 7.0, "c_scale": 5.0}, x=3.5, c=0.0, expected=7.25),
        FormulaTestCase.value(
            params={"k": 10.0, "a": 3.0, "b": 4.0, "c_scale": 1.0}, x=3.3, c=0.0, expected=0.8899999999999988
        ),
        FormulaTestCase.interval_bounds(params={"k": 3.0, "a": 1.0, "b": 2.0, "c_scale": 1.0}, expected=(1.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"k": 5.0, "a": 2.0, "b": 7.0, "c_scale": 5.0}, expected=(2.0, 7.0)),
        FormulaTestCase.interval_bounds(params={"k": 10.0, "a": 3.0, "b": 4.0, "c_scale": 1.0}, expected=(3.0, 4.0)),
    )
