"""This module holds a formula of Sabharwal (2019).

The formula comes from the row with the key ``T2.6`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Sabharwal2019T26(Formula):
    """This formula comes from Sabharwal (2019).

    The survey writes the source's function as ``x^2 + 5*x + 2``; the formula's interval is ``[-6, 0]``.

    No sign change on `[-6, 0]`, which holds both roots, `(-5 - sqrt(17))/2` and `(-5 + sqrt(17))/2`.

    With ``modified = 1``, the interval ``[-6, 0]`` becomes ``[-6, -0.9]``: its upper bound moves left of the second
    root, near -0.44, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with ``c_scale``
    the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 2, 13, 8)
    name = "T2.6"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Sabharwal, C. L. (2019). Blended Root Finding Algorithm Outperforms Bisection and Regula "
            "Falsi Algorithms. Mathematics 7(11), 1118. https://doi.org/10.3390/math7111118."
        ),
        location="T2.6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**2 + 5 * x + 2

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-6.0, 0.0, 6.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-6.0, -0.9, 5.1, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -6.0, "b": 0.0, "c_scale": 6.0, "modified": 0.0}, x=-4.2, c=0.0, expected=-1.3599999999999994
        ),
        FormulaTestCase.value(
            params={"a": -6.0, "b": 0.0, "c_scale": 6.0, "modified": 0.0}, x=-4.2, c=0.25, expected=5.990000000000001
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -6.0, "b": 0.0, "c_scale": 6.0, "modified": 0.0}, expected=(-6.0, 0.0)
        ),
        FormulaTestCase.value(
            params={"a": -6.0, "b": -0.9, "c_scale": 5.1, "modified": 1.0}, x=-4.47, c=0.25, expected=6.280024999999995
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -6.0, "b": -0.9, "c_scale": 5.1, "modified": 1.0}, expected=(-6.0, -0.9)
        ),
    )
