"""This formula is the Heaviside step ``H(x - c) - d``, whose sign changes at the step, where it has no root."""

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


class HeavisideStep(Formula):
    """`HeavisideStep` is ``H(x - c) - d`` on ``[-1, 1]``, with the Heaviside step ``H``: 1 above 0, and 0 at and below.

    The function is ``-d`` up to the step and ``1 - d`` beyond it, so it takes no value 0: its sign changes at the
    step, where it has no root, and bisection converges to the step.

    ``d`` lies between 0 and 1/2. A secant through the 2 bounds crosses 0 at the fraction ``d`` of the interval, so
    ``d`` sets how far from the step an interpolating solver's first step lands. ``d`` and ``1 - d`` give mirror
    images of each other, with x, f and ``c`` negated, so ``d`` stays at or below 1/2. At ``d = 1/2`` the function is
    half the sign function, apart from its value at the step.

    A step has no scale of x, so the interval stays ``[-1, 1]``.

    ``c`` shifts x, so the step lies at ``x = c``.

    References:
        - NIST Digital Library of Mathematical Functions, §1.16(iv), for the definition. https://dlmf.nist.gov/1.16.iv
    """

    number = (2, 7, 1)
    name = "Heaviside step"
    params = (
        FormulaParam(
            "d",
            latex_symbol="d",
            meaning=r"The distance of the lower level below 0; the upper level lies at $1 - \param{d}$.",
        ),
    )
    presentation = FormulaPresentation(
        expression=(
            r"\begin{cases} "
            r"1 - \param{d} & \text{if } \x > \c \\ "
            r"-\param{d} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[-1, 1]",
        summary="The Heaviside step, which changes sign at the step, where it has no root, between 2 levels.",
        param_conditions=(r"$0 < \param{d} \le \frac{1}{2}$",),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate ``H(x - c) - d``."""
        if x > c:
            return 1.0 - d
        else:
            return -d

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe of ``d`` from 2^-16 to 2^-1.

        Below 2^-16 the core solver configs spend about as many evaluations at every ``d``, so the sweep ends there.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("d", -16.0, -1.0, 0.1, ParamNotation.POW2),),
                summary=r"The sweep of $\param{d}$ from $2^{-16}$ to $\frac{1}{2}$.",
            ),
        )

    def is_param_tuple_valid(self, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        return 0.0 < d <= 0.5

    test_cases = (
        FormulaTestCase.value(params={"d": 0.25}, x=0.5, c=0.0, expected=0.75),  # beyond the step
        FormulaTestCase.value(params={"d": 0.25}, x=-0.5, c=0.0, expected=-0.25),  # up to the step
        FormulaTestCase.value(params={"d": 0.25}, x=0.3, c=0.3, expected=-0.25),  # at the step, H(0) = 0
        FormulaTestCase.value(params={"d": 0.5}, x=0.2, c=0.3, expected=-0.5),  # c moves the step to x = c
        FormulaTestCase.invalid(params={"d": 0.0}),
        FormulaTestCase.invalid(params={"d": 0.75}),
        FormulaTestCase.interval_bounds(params={"d": 0.25}, expected=(-1.0, 1.0)),
    )
