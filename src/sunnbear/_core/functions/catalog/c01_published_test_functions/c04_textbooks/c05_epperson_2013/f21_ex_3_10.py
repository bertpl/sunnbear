"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``Ex. 3.10, 3.11, 3.14`` in the survey of published test problems. The
module generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test function.

A person therefore writes this module, starting from the module that the generator writes while the formula is not yet
in the generator's `MODIFIED_FORMULAS`, and a change of the formula's row in `data/literature_test_problems/sources/`
needs a change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Epperson2013Ex310(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^4 - x - 1``; the formula's interval is `[-2, 2]` (Fig. 3.11).

    Real roots 1.22074408460576 and -0.72449195900052, complex roots `-0.24812606280262 ± 1.03398206097597i`. Newton
    from `x0 = 1.25` and `x0 = -0.75`, then deflation (Ex. 3.10, Table 3.7); Durand–Kerner from complex starts (Ex.
    3.11, Table 3.8), and from the real starts 1, -1, 2, -2, where it fails (Ex. 3.14, Table 3.11).

    With ``modified = 1``, the interval ``[-2, 2]`` becomes ``[-2, 1]``: its upper bound moves left of the second root,
    near 1.22, so that the interval holds 1 of the 2 roots. ``c`` shifts x as category 1 states, with ``c_scale`` the
    rounded width of the new interval.

    The published test function fails a benchmark suite's checks of its test functions, because it holds 2 roots, an
    even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 4, 5, 21)
    name = "Ex. 3.10"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="Ex. 3.10, 3.11, 3.14",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return x**4 - x - 1

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-2.0, 2.0, 4.0, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-2.0, 1.0, 3.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, x=-0.8, c=0.0, expected=0.20960000000000015
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, x=-0.8, c=0.25, expected=11.297600000000001
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.0, "b": 2.0, "c_scale": 4.0, "modified": 0.0}, expected=(-2.0, 2.0)
        ),
        FormulaTestCase.value(
            params={"a": -2.0, "b": 1.0, "c_scale": 3.0, "modified": 1.0}, x=-1.1, c=0.25, expected=12.563506250000003
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -2.0, "b": 1.0, "c_scale": 3.0, "modified": 1.0}, expected=(-2.0, 1.0)
        ),
    )
