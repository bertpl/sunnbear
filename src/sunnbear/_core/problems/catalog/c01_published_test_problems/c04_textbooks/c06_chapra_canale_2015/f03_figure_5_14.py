"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Ex. 5.6, §5.3.2, Fig. 5.14; Ex. 6.5; Ex. 7.6; Prob. 5.22, 5.24, 5.25`` in
the survey of published test problems.
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


class ChapraCanale2015Figure514(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``x^10 - 1``; the formula's intervals are `[0, 1.3]`; `[-1.3, 0]` (Ex.
    7.6); `[0, 4]` (the statement of Ex. 7.6).

    Roots 1 and -1. On `[0, 1.3]`, false position converges slowly and bisection beats it (Ex. 5.6); to `es = 0.01%`,
    bisection takes 14 iterations, false position 39 and modified false position 12 (§5.3.2). Newton from `x0 = 0.5`
    jumps to 51.65, then converges slowly (Ex. 6.5). MATLAB's `fzero` on both intervals, and from `x0 = 0`, where it
    finds -1 (Ex. 7.6, whose statement names the interval `[0, 4]`). The problems repeat Ex. 5.6 with the reader's
    programs.
    """

    number = (1, 4, 6, 3)
    name = "Figure 5.14"
    params = (
        FormulaParam("a", latex_symbol="a"),
        FormulaParam("b", latex_symbol="b"),
        FormulaParam("c_scale", latex_symbol="s"),
    )
    location_in_publication = "Example 5.6, §5.3.2, Fig. 5.14; Example 6.5; Example 7.6; Prob. 5.22, 5.24, 5.25"
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \param{c_scale} \c"),),
        expression=r"\tmp{u}^{10} - 1",
        interval=r"[\param{a}, \param{b}]",
        summary=(
            "A function within $10^{-3}$ of $-1$ over the middle half of the stretch between its 2 simple roots and "
            "steep beyond them, with 1 root on each published interval."
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**10 - 1

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=((0.0, 1.3, 1.3), (-1.3, 0.0, 1.3), (0.0, 4.0, 4.0)),
                summary="The published intervals.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"a": 0.0, "b": 1.3, "c_scale": 1.3}, x=0.39, c=0.0, expected=-0.9999185959391481),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 1.3, "c_scale": 1.3}, x=0.91, c=0.25, expected=-0.9953058316511282
        ),
        FormulaTestCase.value(
            params={"a": -1.3, "b": 0.0, "c_scale": 1.3}, x=-0.91, c=0.0, expected=-0.6105838818818924
        ),
        FormulaTestCase.value(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, x=1.2, c=0.0, expected=5.191736422399997),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 1.3, "c_scale": 1.3}, expected=(0.0, 1.3)),
        FormulaTestCase.interval_bounds(params={"a": -1.3, "b": 0.0, "c_scale": 1.3}, expected=(-1.3, 0.0)),
        FormulaTestCase.interval_bounds(params={"a": 0.0, "b": 4.0, "c_scale": 4.0}, expected=(0.0, 4.0)),
    )
