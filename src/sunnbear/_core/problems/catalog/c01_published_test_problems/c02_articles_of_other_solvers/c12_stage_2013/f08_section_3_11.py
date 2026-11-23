"""This module holds a formula of Stage (2013).

The formula comes from the rows with the keys ``3.11`` and ``3.12`` in the survey of published test problems.
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


class Stage2013Section311(Formula):
    """This formula comes from Stage (2013).

    The source prints 2 functions that differ only in the values of some constants; with those constants replaced by
    parameters, the 2 functions become 1 function, ``-d`` if ``x <= 1/3``; ``1 - d`` otherwise:

    - 3.11, with ``d = 0.5``: the survey writes the source's function as ``-0.5`` if ``x <= 1/3``; ``0.5`` otherwise;
      the formula's interval is ``[-10, 10]``
    - 3.12, with ``d = 10^-3``: the survey writes the source's function as ``-10^-3`` if ``x <= 1/3``; ``1 - 10^-3``
      otherwise; the formula's interval is ``[-10, 10]``

    3.11: The article says the function has no actual root, only a discontinuity at ``x = 1/3``.
    """

    number = (1, 2, 12, 8)
    name = "Section 3.11"
    params = (FormulaParam("d", latex_symbol="d"),)
    location_in_publication = "§3.11; §3.12"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - 20 \c"),),
        expression=(
            r"\begin{cases} "
            r"-\param{d} & \text{if } \tmp{u} \le 1/3 \\ "
            r"1 - \param{d} & \text{otherwise} "
            r"\end{cases}"
        ),
        interval="[-10, 10]",
        summary=(
            r"A Heaviside step with no root, only a jump across 0 at $\x = 1/3$, and close to 0 below the jump for "
            r"$\param{d} = 10^{-3}$."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, d: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 20.0 * c
        if x <= 1 / 3:
            return -d
        else:
            return 1 - d

    def interval_bounds(self, d: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-10.0, 10.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("d",), rows=((0.5,), (0.001,)), summary="The published parameter values."),)

    test_cases = (
        FormulaTestCase.value(params={"d": 0.5}, x=-4.0, c=0.0, expected=-0.5),
        FormulaTestCase.value(params={"d": 0.5}, x=-4.0, c=0.25, expected=-0.5),
        FormulaTestCase.value(params={"d": 0.001}, x=-4.0, c=0.0, expected=-0.001),
        FormulaTestCase.value(params={"d": 0.5}, x=5.0, c=0.0, expected=0.5),
        FormulaTestCase.interval_bounds(params={"d": 0.5}, expected=(-10.0, 10.0)),
    )
