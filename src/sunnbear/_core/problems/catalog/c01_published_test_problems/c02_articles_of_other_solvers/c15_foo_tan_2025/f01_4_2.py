"""This module holds a formula of Foo, Tan (2025).

The formula comes from the row with the key ``4.2`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class FooTan202542(Formula):
    """This formula comes from Foo, Tan (2025).

    The survey writes the source's function as ``if(x = 0; 0; -x*log2(x)) - (1 - x)*log2(1 - x) - y``, with the
    parameters ``y = 0.1, 0.2, ..., 0.9``; the formula's interval is ``[0, 0.5]``.

    Definition 1 defines the entropy function on `[0, 1]`, so that `H2(0) = 0`, the limit of `-x*log2(x)` at `x = 0`.
    The row writes that value of the term at `x = 0` as a conditional, and keeps the rest of eq. (6) as printed. Eq.
    (21) prints the 9 roots with 14 decimals, from `0.01298686205551` (`y = 0.1`) to `0.31601934632361` (`y = 0.9`); the
    last decimal of the roots for `y = 0.1` to `0.4` is truncated, not rounded. Starting values solve `4*x*(1 - x) = y`
    or `(4*x*(1 - x))^(1/log(4)) = y`.

    With ``modified = 1``, the formula keeps the published interval, evaluates the published function at x without
    shifting x, and adds ``c`` to the function's value.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because a shift along x by any
    ``c > 0`` evaluates ``log2(x)`` left of ``a = 0``, outside its domain.
    """

    number = (1, 2, 15, 1)
    name = "4.2"
    param_names = ("y", "modified")
    source = FormulaSource(
        reference=(
            "Foo, W. G., Tan, C. H. (2025). Higher-Order Root-Finding Algorithm and its Applications. "
            "arXiv preprint 2509.20897v1. https://doi.org/10.48550/arxiv.2509.20897 "
            "(https://arxiv.org/abs/2509.20897v1)."
        ),
        location="4.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, y: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x`` and add ``c``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - 0.5 * c
            f_offset = 0.0
        else:
            f_offset = c
        return ((0) if (x) == (0) else (-x * math.log2(x))) - (1 - x) * math.log2(1 - x) - y + f_offset

    def interval_bounds(self, y: float, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 0.5)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("y", "modified"),
                rows=(
                    (0.1, 0.0),
                    (0.2, 0.0),
                    (0.3, 0.0),
                    (0.4, 0.0),
                    (0.5, 0.0),
                    (0.6, 0.0),
                    (0.7, 0.0),
                    (0.8, 0.0),
                    (0.9, 0.0),
                ),
            ),
            ParamTable(
                names=("y", "modified"),
                rows=(
                    (0.1, 1.0),
                    (0.2, 1.0),
                    (0.3, 1.0),
                    (0.4, 1.0),
                    (0.5, 1.0),
                    (0.6, 1.0),
                    (0.7, 1.0),
                    (0.8, 1.0),
                    (0.9, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(params={"y": 0.1, "modified": 0.0}, x=0.15, c=0.0, expected=0.5098403047164004),
        FormulaTestCase.value(params={"y": 0.1, "modified": 0.0}, x=0.15, c=0.25, expected=0.06866093149667019),
        FormulaTestCase.value(params={"y": 0.2, "modified": 0.0}, x=0.15, c=0.0, expected=0.4098403047164004),
        FormulaTestCase.value(params={"y": 0.3, "modified": 0.0}, x=0.15, c=0.0, expected=0.3098403047164004),
        FormulaTestCase.value(params={"y": 0.4, "modified": 0.0}, x=0.15, c=0.0, expected=0.20984030471640042),
        FormulaTestCase.value(params={"y": 0.5, "modified": 0.0}, x=0.15, c=0.0, expected=0.10984030471640041),
        FormulaTestCase.value(params={"y": 0.6, "modified": 0.0}, x=0.15, c=0.0, expected=0.00984030471640041),
        FormulaTestCase.value(params={"y": 0.7, "modified": 0.0}, x=0.15, c=0.0, expected=-0.09015969528359959),
        FormulaTestCase.value(params={"y": 0.8, "modified": 0.0}, x=0.15, c=0.0, expected=-0.19015969528359958),
        FormulaTestCase.value(params={"y": 0.9, "modified": 0.0}, x=0.15, c=0.0, expected=-0.2901596952835996),
        FormulaTestCase.value(params={"y": 0.1, "modified": 1.0}, x=0.15, c=0.25, expected=0.7598403047164004),
        FormulaTestCase.value(params={"y": 0.1, "modified": 1.0}, x=0.0, c=-0.25, expected=-0.35),
        FormulaTestCase.interval_bounds(params={"y": 0.1, "modified": 0.0}, expected=(0.0, 0.5)),
    )
