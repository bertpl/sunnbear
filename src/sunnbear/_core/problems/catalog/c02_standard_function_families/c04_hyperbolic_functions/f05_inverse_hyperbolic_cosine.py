"""This formula is the inverse hyperbolic cosine from the edge of its domain, ``acosh(x)/acosh(b) - 0.5 + c``."""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamAxis,
    ParamGrid,
    ParamNotation,
    ParamRecipe,
)


class InverseHyperbolicCosine(Formula):
    """`InverseHyperbolicCosine` is ``acosh(x)/acosh(b) - 0.5 + c`` on ``[1, b]``.

    ``acosh`` is defined from 1 on, so the interval starts at the edge of its domain, where its slope is infinite:
    next to the edge, ``acosh(1 + t)`` is about ``sqrt(2*t)``.

    ``b`` is the upper bound of the interval, any value above 1. For a ``b`` close to 1 the function is close to a
    square root over its whole interval, and for a large ``b`` it grows as a logarithm away from the edge.

    The division by ``acosh(b)`` makes the function -0.5 at the lower bound and 0.5 at the upper bound at ``c = 0``,
    for every ``b``. The root at ``c = 0`` lies at ``x = sqrt((b + 1)/2)``.

    ``c`` adds to the function value, so the root lies at ``x = cosh((0.5 - c)*acosh(b))``.

    References:
        - NIST Digital Library of Mathematical Functions, §4.37, for the definition. https://dlmf.nist.gov/4.37
    """

    number = (2, 4, 5)
    name = "Inverse hyperbolic cosine"
    params = (FormulaParam("b", latex_symbol="b"),)
    presentation = FormulaPresentation(
        expression=r"\frac{\operatorname{arcosh} \x}{\operatorname{arcosh} \param{b}} - 0.5 + \c",
        interval=r"[1, \param{b}]",
        summary="The inverse hyperbolic cosine, with an infinite slope at the lower bound, the edge of its domain.",
        param_conditions=(r"$\param{b} > 1$",),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float) -> float:
        """Evaluate ``acosh(x)/acosh(b) - 0.5 + c``."""
        return math.acosh(x) / math.acosh(b) - 0.5 + c

    def interval_bounds(self, b: float) -> tuple[float, float]:
        """Return the interval ``[1, b]``."""
        return (1.0, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``b`` from 10^0.1 to 10^15.

        The recipe does not leave out the candidates that fail the benchmark suite inclusion conditions. For the
        largest ``b``, the range of ``c`` lets the root come too close to the lower bound to satisfy the conditions,
        so no benchmark suite holds such a candidate.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("b", 0.1, 15.0, 0.1, ParamNotation.POW10),),
                summary=r"The sweep of $\param{b}$ from $10^{0.1}$ to $10^{15}$.",
            ),
        )

    def is_param_tuple_valid(self, b: float) -> bool:
        """Check the conditions that the presentation's `param_conditions` state for a reader."""
        return b > 1.0

    test_cases = (
        FormulaTestCase.value(params={"b": 17.0}, x=3.0, c=0.0, expected=0.0),  # the root, at sqrt((b + 1)/2)
        FormulaTestCase.value(params={"b": 17.0}, x=1.0, c=0.0, expected=-0.5),  # at the edge
        FormulaTestCase.value(params={"b": 17.0}, x=17.0, c=-0.2, expected=0.3),  # c adds to the value
        FormulaTestCase.invalid(params={"b": 1.0}),
        FormulaTestCase.invalid(params={"b": 0.5}),
        FormulaTestCase.interval_bounds(params={"b": 17.0}, expected=(1.0, 17.0)),
    )
