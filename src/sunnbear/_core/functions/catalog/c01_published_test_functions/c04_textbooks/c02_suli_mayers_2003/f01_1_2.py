"""This module holds a formula of Süli, Mayers (2003).

The formula comes from the row with the key ``(1.2)`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class SuliMayers200312(Formula):
    """This formula comes from Süli, Mayers (2003).

    The survey writes the source's function as ``1/2 - 1/(1 + M*abs(x - 1.05))``, with the parameters given per
    interval, on `[0.8, 1.8]`: `M = 200` (Fig. 1.1), `M = 2000, 20000, 200000, 2000000, 20000000` (Remark 1.1); on
    `[1.04999, 1.05001]`: `M = 2000000, 20000000` (Remark 1.1); the formula's intervals are `[0.8, 1.8]`; `[1.04999,
    1.05001]`.

    2 roots, `1.05 - 1/M` and `1.05 + 1/M`, only `2/M` apart. Remark 1.1 asks the reader to plot it in Maple for each
    `M`, and to replot it on the smaller interval for the 2 largest `M`. A footnote in Section 1.6 (p. 28) notes that
    bisection applies although `f` is not differentiable at 1.05.

    With ``modified = 1``, the formula evaluates the published function at ``x + 1.05``, which moves the published
    function's minimum from 1.05 to 0. The modified test functions have their own interval, which holds only the left
    root, ``-1/M``.

    The new interval depends on the published interval:

    - for ``[0.8, 1.8]``, it is ``[-2/M, 0]``, with the root in its middle for every ``M``;
    - for the narrow ``[1.04999, 1.05001]``, used with 2 values of ``M``, it is the left half of that interval
      shifted by -1.05, ``[-1e-5, 0]``.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test functions fail a benchmark suite's checks of its test functions, because each published interval
    holds an even number of roots, ``1.05 - 1/M`` and ``1.05 + 1/M``, so that ``f(a)`` and ``f(b)`` have the same sign.

    The ratio of the narrow published interval's largest bound to its width, about 52,500, is also above the checks'
    limit of 100.
    """

    number = (1, 4, 2, 1)
    name = "(1.2)"
    param_names = ("M", "a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Süli, E., Mayers, D. F. (2003). An Introduction to Numerical Analysis. Cambridge "
            "University Press, Cambridge. https://doi.org/10.1017/CBO9780511801181."
        ),
        location="(1.2)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, M: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x - c_scale*c + 1.05``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 1:
            x = x + 1.05
        return 1 / 2 - 1 / (1 + M * abs(x - 1.05))

    def interval_bounds(self, M: float, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("M", "a", "b", "c_scale", "modified"),
                rows=(
                    (200.0, 0.8, 1.8, 1.0, 0.0),
                    (2000.0, 0.8, 1.8, 1.0, 0.0),
                    (20000.0, 0.8, 1.8, 1.0, 0.0),
                    (200000.0, 0.8, 1.8, 1.0, 0.0),
                    (2000000.0, 0.8, 1.8, 1.0, 0.0),
                    (20000000.0, 0.8, 1.8, 1.0, 0.0),
                    (2000000.0, 1.04999, 1.05001, 2e-05, 0.0),
                    (20000000.0, 1.04999, 1.05001, 2e-05, 0.0),
                ),
            ),
            ParamTable(
                names=("M", "a", "b", "c_scale", "modified"),
                rows=(
                    (200.0, -0.01, 0.0, 0.01, 1.0),
                    (2000.0, -0.001, 0.0, 0.001, 1.0),
                    (20000.0, -0.0001, 0.0, 0.0001, 1.0),
                    (200000.0, -1e-05, 0.0, 1e-05, 1.0),
                    (2000000.0, -1e-06, 0.0, 1e-06, 1.0),
                    (20000000.0, -1e-07, 0.0, 1e-07, 1.0),
                    (2000000.0, -1e-05, 0.0, 1e-05, 1.0),
                    (20000000.0, -1e-05, 0.0, 1e-05, 1.0),
                ),
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.value(
            params={"M": 200.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0},
            x=1.1,
            c=0.0,
            expected=0.4090909090909092,
        ),
        FormulaTestCase.value(
            params={"M": 200.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0},
            x=1.1,
            c=0.25,
            expected=0.47560975609756095,
        ),
        FormulaTestCase.value(
            params={"M": 2000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0},
            x=1.1,
            c=0.0,
            expected=0.4900990099009901,
        ),
        FormulaTestCase.value(
            params={"M": 20000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0},
            x=1.1,
            c=0.0,
            expected=0.499000999000999,
        ),
        FormulaTestCase.value(
            params={"M": 200000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0},
            x=1.1,
            c=0.0,
            expected=0.4999000099990001,
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0},
            x=1.1,
            c=0.0,
            expected=0.499990000099999,
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0},
            x=1.1,
            c=0.0,
            expected=0.499999000001,
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": 1.04999, "b": 1.05001, "c_scale": 2e-05, "modified": 0.0},
            x=1.05,
            c=0.0,
            expected=-0.49999999991118216,
            atol=2e-08,
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": 1.04999, "b": 1.05001, "c_scale": 2e-05, "modified": 0.0},
            x=1.05,
            c=0.0,
            expected=-0.4999999991118216,
            atol=2e-07,
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 200.0, "a": 0.8, "b": 1.8, "c_scale": 1.0, "modified": 0.0}, expected=(0.8, 1.8)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 2000000.0, "a": 1.04999, "b": 1.05001, "c_scale": 2e-05, "modified": 0.0},
            expected=(1.04999, 1.05001),
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 200.0, "a": -0.01, "b": 0.0, "c_scale": 0.01, "modified": 1.0}, expected=(-0.01, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 2000.0, "a": -0.001, "b": 0.0, "c_scale": 0.001, "modified": 1.0}, expected=(-0.001, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 20000.0, "a": -0.0001, "b": 0.0, "c_scale": 0.0001, "modified": 1.0}, expected=(-0.0001, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 200000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05, "modified": 1.0}, expected=(-1e-05, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 2000000.0, "a": -1e-06, "b": 0.0, "c_scale": 1e-06, "modified": 1.0}, expected=(-1e-06, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 20000000.0, "a": -1e-07, "b": 0.0, "c_scale": 1e-07, "modified": 1.0}, expected=(-1e-07, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 2000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05, "modified": 1.0}, expected=(-1e-05, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 20000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05, "modified": 1.0}, expected=(-1e-05, 0.0)
        ),
        FormulaTestCase.value(
            params={"M": 200.0, "a": -0.01, "b": 0.0, "c_scale": 0.01, "modified": 1.0},
            x=-0.007,
            c=0.25,
            expected=0.15517241379310392,
        ),
        FormulaTestCase.value(
            params={"M": 2000.0, "a": -0.001, "b": 0.0, "c_scale": 0.001, "modified": 1.0},
            x=-0.0007,
            c=0.25,
            expected=0.1551724137930944,
        ),
        FormulaTestCase.value(
            params={"M": 20000.0, "a": -0.0001, "b": 0.0, "c_scale": 0.0001, "modified": 1.0},
            x=-7e-05,
            c=0.25,
            expected=0.15517241379289376,
            atol=1e-11,
        ),
        FormulaTestCase.value(
            params={"M": 200000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05, "modified": 1.0},
            x=-7e-06,
            c=0.25,
            expected=0.15517241379194327,
            atol=1e-10,
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": -1e-06, "b": 0.0, "c_scale": 1e-06, "modified": 1.0},
            x=-7e-07,
            c=0.25,
            expected=0.15517241378243837,
            atol=1e-09,
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": -1e-07, "b": 0.0, "c_scale": 1e-07, "modified": 1.0},
            x=-7e-08,
            c=0.25,
            expected=0.15517241389860917,
            atol=1e-08,
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05, "modified": 1.0},
            x=-7e-06,
            c=0.25,
            expected=0.4499999999997561,
            atol=1e-11,
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05, "modified": 1.0},
            x=-7e-06,
            c=0.25,
            expected=0.4947643979057324,
        ),
    )
