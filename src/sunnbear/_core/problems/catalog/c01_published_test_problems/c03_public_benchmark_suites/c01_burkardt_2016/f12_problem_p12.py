"""This module holds a formula of Burkardt (2016).

The formula comes from the row with the key ``p12`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamRecipe,
    ParamTable,
)


class Burkardt2016ProblemP12(Formula):
    """This formula comes from Burkardt (2016).

    The survey writes the source's function as ``-exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x < 1.0);
    ``0.0`` (x = 1.0); ``+exp(log(factor) + log(abs(x - 1.0)) - 1.0/(x - 1.0)^2)`` (x > 1.0), with the parameters
    ``factor = 1000.0``; the formula's intervals are ``[-4.0, 4.1]`` (rang); ``[0.50, 2.0]`` (starts 2 and 1).

    The source's starting points, in order, are ``2.0``, ``0.50`` and ``4.0``.
    """

    number = (1, 3, 1, 12)
    name = "Problem p12"
    params = (
        FormulaParam(
            "factor",
            latex_symbol=r"\mathit{factor}",
            meaning=r"The function's scale: away from $\x = 1$, it equals $\param{factor} (\x - 1) e^{-1/(\x - 1)^2}$.",
        ),
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Problem p12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=(
            r"\begin{cases} "
            r"-\exp\left(\ln \param{factor} + \ln|\tmp{u} - 1| - \frac{1}{(\tmp{u} - 1)^2}\right) "
            r"& \text{if } \tmp{u} < 1 \\ "
            r"0 & \text{if } \tmp{u} = 1 \\ "
            r"\exp\left(\ln \param{factor} + \ln|\tmp{u} - 1| - \frac{1}{(\tmp{u} - 1)^2}\right) & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function with all derivatives 0 at its root, and exactly 0 in floating point on a band 0.073 wide, "
            'referred to in the source as "Flat Stanley".'
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, factor: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        if x < 1.0:
            return -math.exp(math.log(factor) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)
        elif x == 1.0:
            return 0.0
        else:
            return math.exp(math.log(factor) + math.log(abs(x - 1.0)) - 1.0 / (x - 1.0) ** 2)

    def interval_bounds(self, factor: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("factor", "a", "b", "c_scale"),
                rows=((1000.0, -4.0, 4.1, 8.1), (1000.0, 0.5, 2.0, 1.5)),
                summary="The published parameter values and intervals.",
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=-1.57, c=0.0, expected=-2208.918772196994
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=-1.57, c=0.25, expected=-4382.445368656935
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": 0.5, "b": 2.0, "c_scale": 1.5},
            x=0.95,
            c=0.0,
            expected=-9.575847983576841e-173,
            atol=0.0,
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=1.0, c=0.0, expected=0.0
        ),
        FormulaTestCase.value(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, x=1.5, c=0.0, expected=9.15781944436709
        ),
        FormulaTestCase.interval_bounds(
            params={"factor": 1000.0, "a": -4.0, "b": 4.1, "c_scale": 8.1}, expected=(-4.0, 4.1)
        ),
        FormulaTestCase.interval_bounds(
            params={"factor": 1000.0, "a": 0.5, "b": 2.0, "c_scale": 1.5}, expected=(0.5, 2.0)
        ),
    )
