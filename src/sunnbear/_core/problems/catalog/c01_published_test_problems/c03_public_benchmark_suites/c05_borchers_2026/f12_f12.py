"""This module holds a formula of Borchers (2026).

The formula comes from the row with the key ``f12`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Borchers2026F12(Formula):
    """This formula comes from Borchers (2026).

    The survey writes the source's function as ``log(x) + x^2/(2*exp(1)) - 2*x/sqrt(exp(1)) + 1``; the formula's
    intervals are `[1, 3.4]`; `[1.0, 2.5]` (figure of §5.2.3).

    Printed root: `1.64872127070`; §5.2.3 calls it extremely flat around the root, compares 7 solvers at `tol = 1e-15`
    (`fzero` from starting point 2.2), and solves it with `ridders` on [1, 3.4] in 128-bit precision, as `f12a` with
    `exp(m1)` for `exp(1)`, `m1 = Rmpfr::mpfr(1.0, 128)`; it gives the true root as `sqrt(exp(1))`

    With ``modified = 1``, the formula computes the published function in the equivalent form ``log1p(s) - s +
    s**2/2``, with ``s = x/sqrt(exp(1)) - 1``, on the published intervals, and ``c`` shifts x as category 1 states.

    Where ``abs(s) < 1/16``, the formula sums the Taylor series of ``log1p(s) - s + s**2/2``, which is ``s**3/3 - s**4/4
    + s**5/5 - ...``, up to its term in ``s**16``, because near the root, at ``s = 0``, the terms of ``log1p(s) - s +
    s**2/2`` cancel as the terms of the published form do; the first omitted term, in ``s**17``, is smaller than the
    rounding error of the sum.

    Where ``abs(s)`` is 1/16 or more, ``log1p(s) - s + s**2/2`` loses at most about 3 of float64's 16 digits.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 2e-5 of
    the root; the series has no terms that cancel.

    With ``modified = 1``, the modification changes what the test problem tests: the source uses the function to show
    that root finders in float64 locate its root only to about 1e-5 (§5.2.3), and the source finds the root in 128-bit
    precision instead; the modified form is accurate near the root in float64.
    """

    number = (1, 3, 5, 12)
    name = "f12"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            'Borchers, H. W. *pracma Handbook*, chapter 5, "Root Finding". '
            "https://hwborchers.lima-city.de/pracmaHandbook/rootfinding.html, accessed 2026-10-18. The "
            "page is unversioned and gives no author or date; it is on the website of Hans W. Borchers,"
            " the author of the R package pracma. The chapter cites no source for its test problems."
        ),
        location="f12",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``log1p(s) - s + s**2/2``, with ``s = y/sqrt(exp(1)) - 1`` and ``y = x -
        c_scale*c``, or by its series near the root. Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 1:
            s = x / math.sqrt(math.exp(1)) - 1
            if abs(s) < 0.0625:
                # Sum s**3*(1/3 - s*(1/4 - s*(1/5 - ...))) by Horner's scheme, up to the series' term in s**16
                series_over_s_cubed = 0.0
                for k in range(16, 2, -1):
                    series_over_s_cubed = 1 / k - s * series_over_s_cubed
                return s**3 * series_over_s_cubed
            else:
                return math.log1p(s) - s + s**2 / 2
        else:
            return math.log(x) + x**2 / (2 * math.exp(1)) - 2 * x / math.sqrt(math.exp(1)) + 1

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((1.0, 3.4, 2.4, 0.0), (1.0, 2.5, 1.5, 0.0))),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((1.0, 3.4, 2.4, 1.0), (1.0, 2.5, 1.5, 1.0))),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them; the case with `modified = 1` at
    # `x=1.65` is the only one near enough to the root to evaluate the series
    test_cases = (
        FormulaTestCase.value(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4, "modified": 0.0}, x=1.72, c=0.0, expected=2.609079470017915e-05
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4, "modified": 0.0}, x=1.72, c=0.25, expected=-0.01456600694656706
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 2.5, "c_scale": 1.5, "modified": 0.0}, x=1.45, c=0.0, expected=-0.0006420942026751546
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4, "modified": 0.0}, expected=(1.0, 3.4)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.0, "b": 2.5, "c_scale": 1.5, "modified": 0.0}, expected=(1.0, 2.5)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4, "modified": 1.0}, expected=(1.0, 3.4)
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4, "modified": 1.0}, x=1.72, c=0.25, expected=-0.01456600694656706
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 3.4, "c_scale": 2.4, "modified": 1.0},
            x=1.65,
            c=0.0,
            expected=1.5542480440130112e-10,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 1.0, "b": 2.5, "c_scale": 1.5, "modified": 1.0}, expected=(1.0, 2.5)
        ),
        FormulaTestCase.value(
            params={"a": 1.0, "b": 2.5, "c_scale": 1.5, "modified": 1.0}, x=1.45, c=0.25, expected=-0.019154917200661727
        ),
    )
