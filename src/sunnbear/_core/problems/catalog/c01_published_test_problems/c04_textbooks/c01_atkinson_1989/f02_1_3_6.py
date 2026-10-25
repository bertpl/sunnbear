"""This module holds a formula of Atkinson (1989).

The formula comes from the row with the key ``(1.3.6)`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Atkinson1989136(Formula):
    """This formula comes from Atkinson (1989).

    The survey writes the source's function as ``x^3 - 3*x^2 + 3*x - 1``; the formula's intervals are `[0, 2]` (Figure
    1.1); `[0.998, 1.002]` (Figure 1.2).

    Equals `(x - 1)^3`. Chapter 1 evaluates it in single precision: Figure 1.1 graphs it on `[0, 2]`, where it looks
    smooth; at 640 points of `[0.998, 1.002]` the values form a band around 0 (Figure 1.2).

    With ``modified = 1``, the formula evaluates the published function at ``x + 1``, on the published interval shifted
    by -1, which lies around 0: ``[-1, 1]`` for ``[0, 2]``, and ``[-0.002, 0.002]`` for ``[0.998, 1.002]``.

    With ``modified = 2``, the formula computes the function of ``modified = 1`` in the equivalent form ``x**3``, on
    the same interval.

    The test problem on ``[0, 2]`` has a version with ``modified = 1`` only so that its version with ``modified = 2``
    can build on it; the shift alone does not make it satisfy the benchmark suite inclusion conditions.

    With ``modified = 1`` or ``2``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new
    interval.

    The published test problem on ``[0.998, 1.002]`` does not satisfy the benchmark suite inclusion conditions, because
    its interval is narrow around the root at 1: the ratio of the interval's largest bound to its width, about 250, is
    above the conditions' limit of 100.

    The published test problem on ``[0, 2]`` and the test problems with ``modified = 1`` do not satisfy the conditions
    either, because the conditions require bisection to spend a fixed number of evaluations, and bisection stops early
    where a midpoint lands on an exact 0 of f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 1e-5 of
    the root; ``x**3`` has no terms that cancel.

    With ``modified = 2`` on ``[-0.002, 0.002]``, the modification changes what the test problem tests: the source uses
    the interval ``[0.998, 1.002]`` to show the band of noise that rounding gives f around the root (Figure 1.2), and
    ``x**3`` has no such band. ``modified = 1`` keeps the noise.
    """

    number = (1, 4, 1, 2)
    name = "(1.3.6)"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Atkinson, K. E. (1989). An Introduction to Numerical Analysis, 2nd edition. John Wiley & "
            "Sons, New York. ISBN 0-471-62489-6."
        ),
        location="(1.3.6)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x - c_scale*c + 1.0``.

        With ``modified = 2``, evaluate the function of ``modified = 1`` as ``(x - c_scale*c)**3``. Category 1 states
        the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 2:
            return x**3
        else:
            if modified == 1:
                x = x + 1.0
            return x**3 - 3 * x**2 + 3 * x - 1

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.0, 2.0, 2.0, 0.0),
                    (0.998, 1.002, 0.004, 0.0),
                ),
            ),
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (-1.0, 1.0, 2.0, 1.0),
                    (-0.002, 0.002, 0.004, 1.0),
                    (-1.0, 1.0, 2.0, 2.0),
                    (-0.002, 0.002, 0.004, 2.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.0, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, x=0.6, c=0.0, expected=-0.06400000000000002
        ),
        FormulaTestCase.value(
            params={"a": 0.0, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, x=0.6, c=0.25, expected=-0.7290000000000001
        ),
        FormulaTestCase.value(
            params={"a": 0.998, "b": 1.002, "c_scale": 0.004, "modified": 0.0},
            x=1.0014,
            c=0.0,
            expected=2.744000000000399e-09,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.0, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, expected=(0.0, 2.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.998, "b": 1.002, "c_scale": 0.004, "modified": 0.0}, expected=(0.998, 1.002)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -0.002, "b": 0.002, "c_scale": 0.004, "modified": 1.0}, expected=(-0.002, 0.002)
        ),
        FormulaTestCase.value(
            params={"a": -0.002, "b": 0.002, "c_scale": 0.004, "modified": 1.0},
            x=-0.0008,
            c=0.25,
            expected=-5.832000000000231e-09,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 1.0}, expected=(-1.0, 1.0)
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 1.0}, x=-0.4, c=0.25, expected=-0.7290000000000001
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 2.0}, expected=(-1.0, 1.0)
        ),
        FormulaTestCase.value(
            params={"a": -1.0, "b": 1.0, "c_scale": 2.0, "modified": 2.0}, x=-0.4, c=0.25, expected=-0.7290000000000001
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -0.002, "b": 0.002, "c_scale": 0.004, "modified": 2.0}, expected=(-0.002, 0.002)
        ),
        FormulaTestCase.value(
            params={"a": -0.002, "b": 0.002, "c_scale": 0.004, "modified": 2.0},
            x=-0.0008,
            c=0.25,
            expected=-5.832e-09,
        ),
    )
