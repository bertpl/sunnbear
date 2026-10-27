"""This module holds formula f1.99.2.15.1, the modified version of the published formula f1.2.15.1.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.15.1 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedFooTan202542(Formula):
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
    name = "4.2"
    param_names = ("y",)
    source = FormulaSource(
        reference=(
            "Foo, W. G., Tan, C. H. (2025). Higher-Order Root-Finding Algorithm and its Applications. "
            "arXiv preprint 2509.20897v1. https://doi.org/10.48550/arxiv.2509.20897 "
            "(https://arxiv.org/abs/2509.20897v1)."
        ),
        location="4.2",
    )

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
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"y": 0.1}, x=0.15, c=0.25, expected=0.7598403047164004),
        FormulaTestCase.value(params={"y": 0.1}, x=0.0, c=-0.25, expected=-0.35),
    )
