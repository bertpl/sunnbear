"""This module holds a formula of Ellithy (2026).

The formula comes from the row with the key ``38`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Ellithy202638(Formula):
    """This formula comes from Ellithy (2026).

    The survey writes the source's function as ``x^4 + 2*x^3 - 13*x^2 - 14*x + 24``; the formula's interval is ``[-3,
    1]``.

    With ``modified = 1``, the interval ``[-3, 1]`` becomes ``[-3, 0.96]``: its upper bound moves left of the root at 1
    by 1% of the published interval's width, rounded half up to 1 significant digit.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test function does not satisfy the benchmark suite inclusion conditions, because ``f(b)`` is 0 at the
    root ``b = 1``.
    """

    number = (1, 2, 18, 20)
    name = "38"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root "
            "finding. Journal of the Egyptian Mathematical Society 34(1), 91–115. "
            "https://doi.org/10.21608/joems.2026.440115.1078. Code and data: the author's repository "
            "https://github.com/Abdelrhman-Ellithy/hybridroots, at commit "
            "`7f22131ef4e1def3e3928dc6558f46f756d0a5ea`."
        ),
        location="38",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**4 + 2 * x**3 - 13 * x**2 - 14 * x + 24

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-3.0, 1.0, 4.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-3.0, 0.96, 3.96, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -3.0, "b": 1.0, "c_scale": 4.0, "modified": 0.0}, x=-1.8, c=0.0, expected=5.913599999999999
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 1.0, "c_scale": 4.0, "modified": 0.0}, x=-1.8, c=0.25, expected=-21.158399999999997
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -3.0, "b": 1.0, "c_scale": 4.0, "modified": 0.0}, expected=(-3.0, 1.0)
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 0.96, "c_scale": 3.96, "modified": 1.0}, x=-1.812, c=0.25, expected=-21.194394966384
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -3.0, "b": 0.96, "c_scale": 3.96, "modified": 1.0}, expected=(-3.0, 0.96)
        ),
    )
