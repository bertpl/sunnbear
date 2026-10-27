"""This module holds formula f1.99.4.1.2, the modified version of the published formula f1.4.1.2.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.1.2 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedAtkinson1989136(Formula):
    """This formula is the modified version of formula f1.4.1.2, from Atkinson (1989).

    The survey writes the source's function as ``x^3 - 3*x^2 + 3*x - 1``; the published intervals are `[0, 2]` (Figure
    1.1); `[0.998, 1.002]` (Figure 1.2).

    Equals `(x - 1)^3`. Chapter 1 evaluates it in single precision: Figure 1.1 graphs it on `[0, 2]`, where it looks
    smooth; at 640 points of `[0.998, 1.002]` the values form a band around 0 (Figure 1.2).

    The formula evaluates ``x**3``, the published function at ``x + 1``, on the published interval shifted by -1, which
    lies around 0: ``[-1, 1]`` for ``[0, 2]``, and ``[-0.002, 0.002]`` for ``[0.998, 1.002]``. ``c`` shifts x by the
    rule of category 1, with ``c_scale`` the rounded width of the new interval.

    For the test problem on ``[0, 2]``, the shift alone does not make it satisfy the benchmark suite inclusion
    conditions; the formula shifts that interval only so that both test problems share the form ``x**3``.

    The published test problem on ``[0.998, 1.002]`` does not satisfy the benchmark suite inclusion conditions, because
    its interval is narrow around the root at 1: the ratio of the interval's largest bound to its width, about 250, is
    above the conditions' limit of 100.

    The published test problem on ``[0, 2]``, and the published function evaluated at ``x + 1`` on either new interval,
    do not satisfy the conditions either, because the conditions require bisection to spend a fixed number of
    evaluations, and bisection stops early where a midpoint lands on an exact 0 of f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 1e-5 of
    the root; ``x**3`` has no terms that cancel.

    On ``[-0.002, 0.002]``, the modification changes what the test problem tests: the source uses the interval
    ``[0.998, 1.002]`` to show the band of noise that rounding gives f around the root (Figure 1.2), and ``x**3`` has no
    such band. The published function evaluated at ``x + 1`` keeps the noise.
    """

    number = (1, 99, 4, 1, 2)
    name = "(1.3.6)"
    param_names = ("a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="(1.3.6)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c + 1``, as ``(x - c_scale*c)**3``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        return x**3

    def interval_bounds(self, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale"),
                rows=(
                    (-1.0, 1.0, 2.0),
                    (-0.002, 0.002, 0.004),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.interval_bounds(params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, expected=(-1.0, 1.0)),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0}, x=-0.4, c=0.25, expected=-0.7290000000000001
        ),
        FormulaTestCase.interval_bounds(params={"a": -0.002, "b": 0.002, "c_scale": 0.004}, expected=(-0.002, 0.002)),
        FormulaTestCase.value(
            params={"a": -0.002, "b": 0.002, "c_scale": 0.004}, x=-0.0008, c=0.25, expected=-5.832e-09
        ),
    )
