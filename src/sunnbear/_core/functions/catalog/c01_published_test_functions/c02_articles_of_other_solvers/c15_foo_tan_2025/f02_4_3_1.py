"""This module holds a formula of Foo, Tan (2025).

The formula comes from the row with the key ``4.3.1`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write the formula's modified version. A person
therefore writes this module, starting from the generated one, and a change of the formula's row in
`data/literature_test_problems/sources/` needs a change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class FooTan2025431(Formula):
    """This formula comes from Foo, Tan (2025).

    The survey writes the source's function as ``x*log(q - 1)/log(q) - if(x = 0; 0; x*log(x))/log(q) - if(x = 1; 0; (1 -
    x)*log(1 - x))/log(q) - y``, with the parameters `q = 2^127 - 1`; `y = 0.1, 0.2, ..., 0.9`; the formula's interval
    is ``[0, (q - 1)/q]``.

    The article writes `Hq(x) = x*logq(q - 1) - x*logq(x) - (1 - x)*logq(1 - x)` with base-q logarithms. Definition 1
    defines `Hq` on `[0, 1]`, so that the terms `x*logq(x)` and `(1 - x)*logq(1 - x)` are `0` at `x = 0` and at `x = 1`.
    The row writes these 2 values as conditionals, which float64 needs at both bounds, because the upper bound `(q -
    1)/q` rounds to `1`; it keeps the rest of the function as printed. The starting value is `x0 = y`. Table 2's values
    match `q = 2^156`, not the stated `q = 2^127 - 1`; the text and Prop. 10, whose bound `0.0157` is `2/127`, confirm
    `2^127 - 1`, which the row keeps.

    With ``modified = 1``, the formula evaluates the published function at the unshifted x and adds ``c`` to its value,
    on the published interval. The published test functions fail the checks of a benchmark suite's test functions,
    because a shift along x in either direction evaluates a logarithm outside its domain, ``log(x)`` left of ``a = 0``
    or ``log(1 - x)`` right of ``b = 1``.
    """

    number = (1, 2, 15, 2)
    name = "4.3.1"
    param_names = ("q", "y", "modified")
    source = FormulaSource(
        reference=(
            "Foo, W. G., Tan, C. H. (2025). Higher-Order Root-Finding Algorithm and its Applications. "
            "arXiv preprint 2509.20897v1. https://doi.org/10.48550/arxiv.2509.20897 "
            "(https://arxiv.org/abs/2509.20897v1)."
        ),
        location="4.3.1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, q: float, y: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x`` and add ``c``."""
        if modified == 0:
            x = x - 1.0 * c
            f_offset = 0.0
        else:
            f_offset = c
        return (
            x * math.log(q - 1) / math.log(q)
            - ((0) if (x) == (0) else (x * math.log(x))) / math.log(q)
            - ((0) if (x) == (1) else ((1 - x) * math.log(1 - x))) / math.log(q)
            - y
            + f_offset
        )

    def interval_bounds(self, q: float, y: float, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("q", "y", "modified"),
                rows=(
                    (1.7014118346046923e38, 0.1, 0.0),
                    (1.7014118346046923e38, 0.2, 0.0),
                    (1.7014118346046923e38, 0.3, 0.0),
                    (1.7014118346046923e38, 0.4, 0.0),
                    (1.7014118346046923e38, 0.5, 0.0),
                    (1.7014118346046923e38, 0.6, 0.0),
                    (1.7014118346046923e38, 0.7, 0.0),
                    (1.7014118346046923e38, 0.8, 0.0),
                    (1.7014118346046923e38, 0.9, 0.0),
                ),
            ),
            ParamTable(
                names=("q", "y", "modified"),
                rows=(
                    (1.7014118346046923e38, 0.1, 1.0),
                    (1.7014118346046923e38, 0.2, 1.0),
                    (1.7014118346046923e38, 0.3, 1.0),
                    (1.7014118346046923e38, 0.4, 1.0),
                    (1.7014118346046923e38, 0.5, 1.0),
                    (1.7014118346046923e38, 0.6, 1.0),
                    (1.7014118346046923e38, 0.7, 1.0),
                    (1.7014118346046923e38, 0.8, 1.0),
                    (1.7014118346046923e38, 0.9, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.1, "modified": 0.0}, x=0.3, c=0.0, expected=0.2069392984191393
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.1, "modified": 0.0}, x=0.3, c=0.25, expected=-0.04774490584948067
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.2, "modified": 0.0}, x=0.3, c=0.0, expected=0.1069392984191393
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.3, "modified": 0.0}, x=0.3, c=0.0, expected=0.0069392984191393005
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.4, "modified": 0.0}, x=0.3, c=0.0, expected=-0.0930607015808607
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.5, "modified": 0.0}, x=0.3, c=0.0, expected=-0.1930607015808607
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.6, "modified": 0.0}, x=0.3, c=0.0, expected=-0.29306070158086067
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.7, "modified": 0.0}, x=0.3, c=0.0, expected=-0.3930607015808607
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.8, "modified": 0.0}, x=0.3, c=0.0, expected=-0.4930607015808607
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.9, "modified": 0.0}, x=0.3, c=0.0, expected=-0.5930607015808607
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.1, "modified": 1.0}, x=0.3, c=0.25, expected=0.4569392984191393
        ),
        FormulaTestCase.value(
            params={"q": 1.7014118346046923e38, "y": 0.1, "modified": 1.0}, x=1.0, c=-0.25, expected=0.65
        ),
        FormulaTestCase.interval_bounds(
            params={"q": 1.7014118346046923e38, "y": 0.1, "modified": 0.0}, expected=(0.0, 1.0)
        ),
    )
