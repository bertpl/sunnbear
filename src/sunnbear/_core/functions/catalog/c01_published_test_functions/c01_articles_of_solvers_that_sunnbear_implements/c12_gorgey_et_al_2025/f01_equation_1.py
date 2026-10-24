"""This module holds a formula of Gorgey et al. (2025).

The formula comes from the row with the key ``Equation 1`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class GorgeyEtAl2025Equation1(Formula):
    """This formula comes from Gorgey et al. (2025).

    The survey writes the source's function as ``(x + 2)*(x + 1)*(x - 3)^3``; the formula's intervals are `[-2.5, 3]`;
    `[2, 3.5]` (Figure 1's caption and the text below Table 2).

    Roots `-2`, `-1` and `3`; the text names `3` as the root found.

    With ``modified = 1``, the interval ``[-2.5, 3]`` becomes ``[-2.5, 3.06]``: its upper bound moves right of the
    triple root at 3 by 1% of the published interval's width, rounded half up to 1 significant digit, so that ``b`` is
    not a root and the interval holds all 3 roots, -2, -1 and 3.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test function on ``[-2.5, 3]`` does not satisfy the benchmark suite inclusion conditions, because
    ``f(b)`` is 0 at the triple root ``b = 3``.
    """

    number = (1, 1, 12, 1)
    name = "Equation 1"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Gorgey, A., Azim, F. A., Zulkifly, Z. H., Hassim, H. (2025). Efficiency of Ridders' method"
            " in solving nonlinear equations using Scilab programming. Data Analytics and Applied "
            "Mathematics 6(1), 23–35. https://doi.org/10.15282/daam.v6i1.11307."
        ),
        location="Equation 1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x + 2) * (x + 1) * (x - 3) ** 3

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (-2.5, 3.0, 5.5, 0.0),
                    (2.0, 3.5, 1.5, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-2.5, 3.06, 5.56, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -2.5, "b": 3.0, "c_scale": 5.5, "modified": 0.0}, x=-0.85, c=0.0, expected=-9.843992812500002
        ),
        FormulaTestCase.value(
            params={"a": -2.5, "b": 3.0, "c_scale": 5.5, "modified": 0.0}, x=-0.85, c=0.25, expected=-39.316739150390646
        ),
        FormulaTestCase.value(
            params={"a": 2.0, "b": 3.5, "c_scale": 1.5, "modified": 0.0}, x=2.45, c=0.0, expected=-2.554272187499998
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.5, "b": 3.0, "c_scale": 5.5, "modified": 0.0}, expected=(-2.5, 3.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 2.0, "b": 3.5, "c_scale": 1.5, "modified": 0.0}, expected=(2.0, 3.5)
        ),
        FormulaTestCase.value(
            params={"a": -2.5, "b": 3.06, "c_scale": 5.56, "modified": 1.0},
            x=-0.832,
            c=0.25,
            expected=-38.63089614110562,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.5, "b": 3.06, "c_scale": 5.56, "modified": 1.0}, expected=(-2.5, 3.06)
        ),
    )
