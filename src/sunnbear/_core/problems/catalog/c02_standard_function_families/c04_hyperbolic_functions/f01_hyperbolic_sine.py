"""This formula is the hyperbolic sine, shifted by ``c`` along x, ``sinh(x - c)``."""

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


class HyperbolicSine(Formula):
    """`HyperbolicSine` is ``sinh(x - c)`` on ``[-b, b]``.

    ``b`` is the upper bound of the interval, any value above 0. The function is close to the line ``x - c`` for a
    small ``b``, and grows as an exponential toward both bounds for a large ``b``.

    ``c`` shifts x, so the root lies at ``x = c``. For a large ``b``, a shift by ``c`` multiplies the value at 1 bound
    by about ``exp(abs(c))`` and divides the value at the other bound by the same factor.

    References:
        - NIST Digital Library of Mathematical Functions, §4.28, for the definition. https://dlmf.nist.gov/4.28
    """

    number = (2, 4, 1)
    name = "Hyperbolic sine"
    params = (FormulaParam("b", latex_symbol="b"),)
    presentation = FormulaPresentation(
        expression=r"\sinh(\x - \c)",
        interval=r"[-\param{b}, \param{b}]",
        summary=(
            "The hyperbolic sine, from nearly a line on a narrow interval to exponential growth toward both bounds on "
            "a wide one."
        ),
        param_conditions=(r"$\param{b} > 0$",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float) -> float:
        """Evaluate ``sinh(x - c)``."""
        return math.sinh(x - c)

    def interval_bounds(self, b: float) -> tuple[float, float]:
        """Return the interval ``[-b, b]``."""
        return (-b, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``b`` from 10^-1 to 10^2.

        At the low end the function is a line to within 0.2 %. At the high end its values at the bounds are about
        1.3e43.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("b", -1.0, 2.0, 0.02, ParamNotation.POW10),),
                summary=r"The sweep of $\param{b}$ from $10^{-1}$ to $10^{2}$.",
            ),
        )

    def is_param_tuple_valid(self, b: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return b > 0.0

    test_cases = (
        FormulaTestCase.value(params={"b": 1.0}, x=0.0, c=0.0, expected=0.0),  # the root, at x = c
        FormulaTestCase.value(params={"b": 1.0}, x=0.5, c=0.5, expected=0.0),
        FormulaTestCase.value(params={"b": 10.0}, x=10.0, c=0.0, expected=math.sinh(10.0)),
        FormulaTestCase.value(params={"b": 10.0}, x=-10.0, c=1.0, expected=-math.sinh(11.0)),  # c shifts x
        FormulaTestCase.invalid(params={"b": 0.0}),
        FormulaTestCase.invalid(params={"b": -1.0}),
        FormulaTestCase.interval_bounds(params={"b": 10.0}, expected=(-10.0, 10.0)),
    )
