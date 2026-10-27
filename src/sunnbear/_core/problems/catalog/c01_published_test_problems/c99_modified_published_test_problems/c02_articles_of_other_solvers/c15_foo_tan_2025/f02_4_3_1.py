"""This module holds formula f1.99.2.15.2, the modified version of the published formula f1.2.15.2.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.2.15.2 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedFooTan2025431(Formula):
    """This formula is the modified version of formula f1.2.15.2, from Foo, Tan (2025).

    The survey writes the source's function as ``x*log(q - 1)/log(q) - if(x = 0; 0; x*log(x))/log(q) - if(x = 1; 0; (1 -
    x)*log(1 - x))/log(q) - y``, with the parameters `q = 2^127 - 1`; `y = 0.1, 0.2, ..., 0.9`; the published interval
    is ``[0, (q - 1)/q]``.

    The article writes `Hq(x) = x*logq(q - 1) - x*logq(x) - (1 - x)*logq(1 - x)` with base-q logarithms. Definition 1
    defines `Hq` on `[0, 1]`, so that the terms `x*logq(x)` and `(1 - x)*logq(1 - x)` are `0` at `x = 0` and at `x = 1`.
    The row writes these 2 values as conditionals, which float64 needs at both bounds, because the upper bound `(q -
    1)/q` rounds to `1`; it keeps the rest of the function as printed. The starting value is `x0 = y`. Table 2's values
    match `q = 2^156`, not the stated `q = 2^127 - 1`; the text and Prop. 10, whose bound `0.0157` is `2/127`, confirm
    `2^127 - 1`, which the row keeps.

    The formula keeps the published interval, evaluates the published function at x without shifting x, and adds ``c``
    to the function's value.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because a shift along x in
    either direction evaluates a logarithm outside its domain, ``log(x)`` left of ``a = 0`` or ``log(1 - x)`` right of
    ``b = 1``.
    """

    number = (1, 99, 2, 15, 2)
    name = "4.3.1"
    param_names = ("q", "y")
    source = FormulaSource(
        reference=(
            "Foo, W. G., Tan, C. H. (2025). Higher-Order Root-Finding Algorithm and its Applications. "
            "arXiv preprint 2509.20897v1. https://doi.org/10.48550/arxiv.2509.20897 "
            "(https://arxiv.org/abs/2509.20897v1)."
        ),
        location="4.3.1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, q: float, y: float) -> float:
        """Evaluate the published function at ``x``, and add ``c``."""
        return (
            x * math.log(q - 1) / math.log(q)
            - ((0) if (x) == (0) else (x * math.log(x))) / math.log(q)
            - ((0) if (x) == (1) else ((1 - x) * math.log(1 - x))) / math.log(q)
            - y
            + c
        )

    def interval_bounds(self, q: float, y: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("q", "y"),
                rows=(
                    (1.7014118346046923e38, 0.1),
                    (1.7014118346046923e38, 0.2),
                    (1.7014118346046923e38, 0.3),
                    (1.7014118346046923e38, 0.4),
                    (1.7014118346046923e38, 0.5),
                    (1.7014118346046923e38, 0.6),
                    (1.7014118346046923e38, 0.7),
                    (1.7014118346046923e38, 0.8),
                    (1.7014118346046923e38, 0.9),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.1}, x=0.3, c=0.25, expected=0.4569392984191393
        ),
        FormulaTestCase.value(params={"q": 1.7014118346046923e38, "y": 0.1}, x=1.0, c=-0.25, expected=0.65),
    )
