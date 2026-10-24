"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``P38(a)`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Atkinson1989P38A(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``x^4 - 5.7*x^3 - 0.47*x^2 + 29.865*x - 26.1602``; the formula's interval
    is ``[-3, 5]``.

    Evaluated in single and double precision, in steps of `h = 0.1`, to measure the noise; P41 finds the roots with a
    polynomial package.

    With ``modified = 1``, the interval ``[-3, 5]`` becomes ``[-3, 4]``: its upper bound moves left of the last root,
    near 4.7, so that the interval holds 3 of the 4 roots. ``c`` shifts x as category 1 states, with ``c_scale`` the
    rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because it holds 4 roots, an
    even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 1, 8)
    name = "P38(a)"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="P38(a)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**4 - 5.7 * x**3 - 0.47 * x**2 + 29.865 * x - 26.1602

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-3.0, 5.0, 8.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-3.0, 4.0, 7.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -3.0, "b": 5.0, "c_scale": 8.0, "modified": 0.0}, x=-0.6, c=0.0, expected=-42.8876
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 5.0, "c_scale": 8.0, "modified": 0.0}, x=-0.6, c=0.25, expected=38.89440000000001
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -3.0, "b": 5.0, "c_scale": 8.0, "modified": 0.0}, expected=(-3.0, 5.0)
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 4.0, "c_scale": 7.0, "modified": 1.0}, x=-0.9, c=0.25, expected=46.787343749999984
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -3.0, "b": 4.0, "c_scale": 7.0, "modified": 1.0}, expected=(-3.0, 4.0)
        ),
    )
