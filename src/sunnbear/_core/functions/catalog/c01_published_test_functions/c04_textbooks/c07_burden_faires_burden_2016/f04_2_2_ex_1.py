"""This module holds a formula of Burden, Faires, Burden (2016).

The formula comes from the row with the key ``§2.2 Ex. 1; Fig. 2.2`` in the survey of published test problems. The
module generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class BurdenFairesBurden201622Ex1(Formula):
    """This formula comes from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x = x^2 - 2``; the formula's interval is `[-3, 3]` (Fig. 2.2).

    Fixed points -1 and 2, from `(p + 1)*(p - 2) = 0`.

    With ``modified = 1``, the interval ``[-3, 3]`` becomes ``[-3, 1]``: its upper bound moves left of the second root
    at 2, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with ``c_scale`` the rounded
    width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because it holds 2 roots, an
    even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 7, 4)
    name = "§2.2 Ex. 1"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="§2.2 Ex. 1; Fig. 2.2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x) - (x**2 - 2)

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-3.0, 3.0, 6.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-3.0, 1.0, 4.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -3.0, "b": 3.0, "c_scale": 6.0, "modified": 0.0}, x=-1.2, c=0.0, expected=-0.6399999999999999
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 3.0, "c_scale": 6.0, "modified": 0.0}, x=-1.2, c=0.25, expected=-7.990000000000001
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -3.0, "b": 3.0, "c_scale": 6.0, "modified": 0.0}, expected=(-3.0, 3.0)
        ),
        FormulaTestCase.value(
            params={"a": -3.0, "b": 1.0, "c_scale": 4.0, "modified": 1.0}, x=-1.8, c=0.25, expected=-8.639999999999999
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -3.0, "b": 1.0, "c_scale": 4.0, "modified": 1.0}, expected=(-3.0, 1.0)
        ),
    )
