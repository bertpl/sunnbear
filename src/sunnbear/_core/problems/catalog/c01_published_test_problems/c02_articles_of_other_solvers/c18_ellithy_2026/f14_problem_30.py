"""This module holds a formula of Ellithy (2026).

The formula comes from the rows with the keys ``30`` and ``31`` in the survey of published test problems.
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


class Ellithy2026Problem30(Formula):
    """This formula comes from Ellithy (2026).

    The source prints 1 function in 2 rows, each on its own interval:

    - 30: the survey writes the source's function as ``(x - 1)*(x - 2)*...*(x - 20)``; the formula's interval is ``[0,
      1.5]``
    - 31: the survey writes the source's function as ``(x - 1)*(x - 2)*...*(x - 20)``; the formula's interval is ``[19,
      21]``

    The function is Wilkinson's polynomial, which the author's file writes out as the product of all 20 factors ``(x -
    1)`` to ``(x - 20)``.
    """

    number = (1, 2, 18, 14)
    name = "Problem 30"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "dataset.json, problems 30 and 31"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\prod_{i=1}^{20} (\tmp{u} - i)",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "Wilkinson's polynomial, above $10^{15}$ in magnitude over most of each interval, with 1 root on the lower "
            "interval and 2 on the upper."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        # the loop multiplies the 20 factors (x - 1) to (x - 20) from the left, in the order of the author's file
        product = x - 1
        for i in range(2, 21):
            product *= x - i
        return product

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.5, 1.5), (19.0, 21.0, 2.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 1.5, "c_scale": 1.5}, x=0.45, c=0.0, expected=3.8859900569265306e17
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 1.5, "c_scale": 1.5}, x=0.45, c=0.25, expected=1.848893119048187e18
        ),
        FormulaTestCase.value(
            params={"a": 19.0, "b": 21.0, "c_scale": 2.0}, x=19.6, c=0.0, expected=-9999185058305838.0
        ),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.5, "c_scale": 1.5}, expected=(0.0, 1.5)),
        FormulaTestCase.interval_bounds(params={"a": 19.0, "b": 21.0, "c_scale": 2.0}, expected=(19.0, 21.0)),
    )
