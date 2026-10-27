"""This module holds formula f1.99.4.2.5, the modified version of the published formula f1.4.2.5.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.2.5 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedSuliMayers2003133(Formula):
    """This formula is the modified version of formula f1.4.2.5, from Süli, Mayers (2003).

    The survey writes the source's function as ``x = a*x*(1 - x)``, with the parameters `0 < a <= 4`; `a = 3.4, 3.5,
    3.99`; the published interval is ``[0, 1]``.

    The formula's parameter ``a_`` is the source's ``a``, renamed because ``[a, b]`` names the formula's interval.

    Fixed points 0 and `1 - 1/a`. For `a = 3.4` the iterates approach a 2-cycle, 0.45 and 0.84, the 2 stable fixed
    points of `g(g(x))` (eq. (1.34)); for `a = 3.5` a 4-cycle; for `a = 3.99`, from `x0 = 0.75`, no regular pattern.

    The formula changes the published interval ``[0, 1]`` to ``[0.01, 1]``: its lower bound moves right of the root at
    0 by 1% of the published interval's width, rounded half up to 1 significant digit.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    Each published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` is 0 at the
    root ``a = 0``.
    """

    number = (1, 99, 4, 2, 5)
    name = "(1.33)"
    param_names = ("a_", "a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Süli, E., Mayers, D. F. (2003). An Introduction to Numerical Analysis. Cambridge "
            "University Press, Cambridge. https://doi.org/10.1017/CBO9780511801181."
        ),
        location="(1.33)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x) - (a_ * x * (1 - x))

    def interval_bounds(self, a_: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a_", "a", "b", "c_scale"),
                rows=(
                    (3.4, 0.01, 1.0, 0.99),
                    (3.5, 0.01, 1.0, 0.99),
                    (3.99, 0.01, 1.0, 0.99),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a_": 3.4, "a": 0.01, "b": 1.0, "c_scale": 0.99}, x=0.307, c=0.25, expected=-0.13076315
        ),
        FormulaTestCase.value(
            params={"a_": 3.5, "a": 0.01, "b": 1.0, "c_scale": 0.99}, x=0.307, c=0.25, expected=-0.136359125
        ),
        FormulaTestCase.value(
            params={"a_": 3.99, "a": 0.01, "b": 1.0, "c_scale": 0.99}, x=0.307, c=0.25, expected=-0.1637794025
        ),
        FormulaTestCase.interval_bounds(params={"a_": 3.4, "a": 0.01, "b": 1.0, "c_scale": 0.99}, expected=(0.01, 1.0)),
        FormulaTestCase.interval_bounds(params={"a_": 3.5, "a": 0.01, "b": 1.0, "c_scale": 0.99}, expected=(0.01, 1.0)),
        FormulaTestCase.interval_bounds(
            params={"a_": 3.99, "a": 0.01, "b": 1.0, "c_scale": 0.99}, expected=(0.01, 1.0)
        ),
    )
