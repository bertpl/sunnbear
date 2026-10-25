"""This module holds a formula of Süli, Mayers (2003).

The formula comes from the row with the key ``(1.33)`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class SuliMayers2003133(Formula):
    """This formula comes from Süli, Mayers (2003).

    The survey writes the source's function as ``x = a*x*(1 - x)``, with the parameters `0 < a <= 4`; `a = 3.4, 3.5,
    3.99`; the formula's interval is ``[0, 1]``.

    The formula's parameter ``a_`` is the source's ``a``, renamed because ``[a, b]`` names the formula's interval.

    Fixed points 0 and `1 - 1/a`. For `a = 3.4` the iterates approach a 2-cycle, 0.45 and 0.84, the 2 stable fixed
    points of `g(g(x))` (eq. (1.34)); for `a = 3.5` a 4-cycle; for `a = 3.99`, from `x0 = 0.75`, no regular pattern.

    With ``modified = 1``, the interval ``[0, 1]`` becomes ``[0.01, 1]``: its lower bound moves right of the root at 0
    by 1% of the published interval's width, rounded half up to 1 significant digit.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    Each published test problem does not satisfy the benchmark suite inclusion conditions, because ``f(a)`` is 0 at the
    root ``a = 0``.
    """

    number = (1, 4, 2, 5)
    name = "(1.33)"
    param_names = ("a_", "a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Süli, E., Mayers, D. F. (2003). An Introduction to Numerical Analysis. Cambridge "
            "University Press, Cambridge. https://doi.org/10.1017/CBO9780511801181."
        ),
        location="(1.33)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a_: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return (x) - (a_ * x * (1 - x))

    def interval_bounds(self, a_: float, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a_", "a", "b", "c_scale", "modified"),
                rows=(
                    (3.4, 0.0, 1.0, 1.0, 0.0),
                    (3.5, 0.0, 1.0, 1.0, 0.0),
                    (3.99, 0.0, 1.0, 1.0, 0.0),
                ),
            ),
            ParamTable(
                names=("a_", "a", "b", "c_scale", "modified"),
                rows=(
                    (3.4, 0.01, 1.0, 0.99, 1.0),
                    (3.5, 0.01, 1.0, 0.99, 1.0),
                    (3.99, 0.01, 1.0, 0.99, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a_": 3.4, "a": 0.0, "b": 1.0, "c_scale": 1.0, "modified": 0.0}, x=0.3, c=0.0, expected=-0.414
        ),
        FormulaTestCase.value(
            params={"a_": 3.4, "a": 0.0, "b": 1.0, "c_scale": 1.0, "modified": 0.0},
            x=0.3,
            c=0.25,
            expected=-0.11149999999999997,
        ),
        FormulaTestCase.value(
            params={"a_": 3.5, "a": 0.0, "b": 1.0, "c_scale": 1.0, "modified": 0.0}, x=0.3, c=0.0, expected=-0.435
        ),
        FormulaTestCase.value(
            params={"a_": 3.99, "a": 0.0, "b": 1.0, "c_scale": 1.0, "modified": 0.0}, x=0.3, c=0.0, expected=-0.5379
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 3.4, "a": 0.0, "b": 1.0, "c_scale": 1.0, "modified": 0.0}, expected=(0.0, 1.0)
        ),
        FormulaTestCase.value(
            params={"a_": 3.4, "a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 1.0},
            x=0.307,
            c=0.25,
            expected=-0.13076315,
        ),
        FormulaTestCase.value(
            params={"a_": 3.5, "a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 1.0},
            x=0.307,
            c=0.25,
            expected=-0.136359125,
        ),
        FormulaTestCase.value(
            params={"a_": 3.99, "a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 1.0},
            x=0.307,
            c=0.25,
            expected=-0.1637794025,
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 3.4, "a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 1.0}, expected=(0.01, 1.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 3.5, "a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 1.0}, expected=(0.01, 1.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a_": 3.99, "a": 0.01, "b": 1.0, "c_scale": 0.99, "modified": 1.0}, expected=(0.01, 1.0)
        ),
    )
