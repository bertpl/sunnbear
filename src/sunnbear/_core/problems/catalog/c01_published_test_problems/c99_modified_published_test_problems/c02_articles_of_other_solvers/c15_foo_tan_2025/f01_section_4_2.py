"""This module holds formula f1.99.2.15.1, the modified version of the published formula f1.2.15.1.

A change of formula f1.2.15.1 may need a matching change of this module.
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


class ModifiedFooTan2025Section42(Formula):
    """This formula is the modified version of formula f1.2.15.1, from Foo, Tan (2025).

    The survey writes the source's function as ``if(x = 0; 0; -x*log2(x)) - (1 - x)*log2(1 - x) - y``, with the
    parameters ``y = 0.1, 0.2, ..., 0.9``; the published interval is ``[0, 0.5]``.

    Definition 1 defines the entropy function on `[0, 1]`, so that `H2(0) = 0`, the limit of `-x*log2(x)` at `x = 0`.
    The row writes that value of the term at `x = 0` as a conditional, and keeps the rest of eq. (6) as printed. Eq.
    (21) prints the 9 roots with 14 decimals, from `0.01298686205551` (`y = 0.1`) to `0.31601934632361` (`y = 0.9`); the
    last decimal of the roots for `y = 0.1` to `0.4` is truncated, not rounded. Starting values solve `4*x*(1 - x) = y`
    or `(4*x*(1 - x))^(1/log(4)) = y`.

    The formula keeps the published interval, evaluates the published function at x without shifting x, and adds ``c``
    to the function's value.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because a shift along x by any
    ``c > 0`` evaluates ``log2(x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 99, 2, 15, 1)
    name = "Section 4.2"
    params = (FormulaParam("y", latex_symbol="y"),)
    location_in_publication = "Section 4.2"
    presentation = FormulaPresentation(
        expression=(
            r"\begin{cases} 0 & \text{for}\: \x = 0 \\- \x \log_{2}{\left(\x \right)} & "
            r"\text{otherwise} \end{cases} - \left(1 - \x\right) \log_{2}{\left(1 - \x \right)} - "
            r"\param{y} + \c"
        ),
        interval="[0, 0.5]",
        summary=(
            r"The binary entropy function minus $\param{y}$, with 1 root, 0.013 above the lower bound at $\param{y} = "
            r"0.1$, and a slope that grows like $-\log_2(\x)$ toward that bound."
        ),
        notes=(
            (
                r"$\c$ shifts the function along the y-axis, not along x as for the published test "
                r"problems, because a shift along x by any $\c > 0$ evaluates $\log_2(\x)$ left of 0, "
                "outside its domain."
            ),
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_Y

    @staticmethod
    def parametrized_fun(x: float, c: float, y: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return ((0) if (x) == (0) else (-x * math.log2(x))) - (1 - x) * math.log2(1 - x) - y + c

    def interval_bounds(self, y: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("y",),
                rows=(
                    (0.1,),
                    (0.2,),
                    (0.3,),
                    (0.4,),
                    (0.5,),
                    (0.6,),
                    (0.7,),
                    (0.8,),
                    (0.9,),
                ),
                summary="The published parameter values.",
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"y": 0.1}, x=0.15, c=0.25, expected=0.7598403047164004),
        FormulaTestCase.value(params={"y": 0.1}, x=0.0, c=-0.25, expected=-0.35),
    )
