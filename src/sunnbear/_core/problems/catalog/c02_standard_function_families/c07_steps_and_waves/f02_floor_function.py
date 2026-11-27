"""This formula is the staircase ``floor(x - n*c) + 1/2``, whose sign changes at 1 of its ``2*n + 1`` steps."""

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
    ParamRounding,
)


class FloorFunction(Formula):
    """`FloorFunction` is ``floor(x - n*c) + 1/2`` on ``[-(n + 1/2), n + 1/2]``.

    Each step has height 1 and width 1, and the function takes only the values ``k + 1/2`` for integers ``k``, so it
    takes no value 0: its sign changes at the step from -1/2 to 1/2, where it has no root, and bisection converges to
    that step.

    ``n`` is an integer of at least 1: the number of further steps on each side of that step. The bounds lie halfway
    along a step. Across many steps, the function is close to the line ``x - n*c``, so an interpolating solver first
    finds the right step in a few evaluations and then meets the jump; the more steps, the more of bisection's halvings
    that first part saves. At ``n = 0`` the formula would be the Heaviside step at ``d = 1/2``.

    ``c`` shifts x by ``n*c``, so the c-range is close to the same for every ``n``, and the step of the sign change lies
    at ``x = n*c``.

    References:
        - NIST Digital Library of Mathematical Functions, Common Notations and Definitions, for the definition.
          https://dlmf.nist.gov/front/introduction#common
    """

    number = (2, 7, 2)
    name = "Floor function"
    params = (
        FormulaParam(
            "n",
            latex_symbol="n",
            meaning=r"The number of steps on each side of the step at which the sign changes.",
        ),
    )
    presentation = FormulaPresentation(
        expression=r"\left\lfloor \x - \param{n} \c \right\rfloor + \frac{1}{2}",
        interval=r"\left[-\left(\param{n} + \frac{1}{2}\right), \param{n} + \frac{1}{2}\right]",
        summary=(
            "The floor function, a staircase of steps of height 1 that changes sign at 1 step, where it has no root, "
            "and is close to a line across many steps."
        ),
        param_conditions=(r"$\param{n}$ is an integer of at least 1",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate ``floor(x - n*c) + 1/2``."""
        return math.floor(x - n * c) + 0.5

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the interval ``[-(n + 1/2), n + 1/2]``."""
        return (-(n + 0.5), n + 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe of the integers ``n`` nearest to 2^(0.1*i), for i from 0 to 210.

        The sweep ends at ``n = 2^21``, where the core solver configs spend about half of bisection's evaluations;
        more steps make the function easier still.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("n", 0.0, 21.0, 0.1, ParamNotation.POW2, ParamRounding.NEAREST_INTEGER),),
                summary=r"The values of $\param{n}$ nearest to $2^{0.1 i}$, for $i$ from 0 to 210, each once.",
            ),
        )

    def is_param_tuple_valid(self, n: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return n >= 1.0 and n == math.floor(n)

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0}, x=0.5, c=0.0, expected=0.5),  # beyond the step of the sign change
        FormulaTestCase.value(params={"n": 2.0}, x=-0.5, c=0.0, expected=-0.5),  # up to it
        FormulaTestCase.value(params={"n": 2.0}, x=0.0, c=0.0, expected=0.5),  # at the step, floor(0) = 0
        FormulaTestCase.value(params={"n": 2.0}, x=2.25, c=0.0, expected=2.5),  # the top step
        FormulaTestCase.value(params={"n": 4.0}, x=1.9, c=0.5, expected=-0.5),  # c moves the step to x = n*c = 2
        FormulaTestCase.invalid(params={"n": 0.0}),
        FormulaTestCase.invalid(params={"n": 1.5}),
        FormulaTestCase.interval_bounds(params={"n": 2.0}, expected=(-2.5, 2.5)),
    )
