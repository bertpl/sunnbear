"""This module holds formula f1.99.4.2.1, the modified version of the published formula f1.4.2.1.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.2.1 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedSuliMayers200312(Formula):
    """This formula is the modified version of formula f1.4.2.1, from Süli, Mayers (2003).

    The survey writes the source's function as ``1/2 - 1/(1 + M*abs(x - 1.05))``, with the parameters given per
    interval, on `[0.8, 1.8]`: `M = 200` (Fig. 1.1), `M = 2000, 20000, 200000, 2000000, 20000000` (Remark 1.1); on
    `[1.04999, 1.05001]`: `M = 2000000, 20000000` (Remark 1.1); the published intervals are `[0.8, 1.8]`; `[1.04999,
    1.05001]`.

    2 roots, `1.05 - 1/M` and `1.05 + 1/M`, only `2/M` apart. Remark 1.1 asks the reader to plot it in Maple for each
    `M`, and to replot it on the smaller interval for the 2 largest `M`. A footnote in Section 1.6 (p. 28) notes that
    bisection applies although `f` is not differentiable at 1.05.

    The formula evaluates the published function at ``x + 1.05``, which moves the published function's minimum from
    1.05 to 0. The modified test problems have their own interval, which holds only the left root, ``-1/M``.

    The new interval depends on the published interval:

    - for ``[0.8, 1.8]``, it is ``[-2/M, 0]``, with the root in its middle for every ``M``;
    - for the narrow ``[1.04999, 1.05001]``, used with 2 values of ``M``, it is the left half of that interval
      shifted by -1.05, ``[-1e-5, 0]``.

    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the new interval.

    The published test problems do not satisfy the benchmark suite inclusion conditions, because each published
    interval holds an even number of roots, ``1.05 - 1/M`` and ``1.05 + 1/M``, so that ``f(a)`` and ``f(b)`` have the
    same sign.

    The ratio of the narrow published interval's largest bound to its width, about 52,500, is also above the conditions'
    limit of 100.

    The modification changes what the test problem tests: the source uses the function to show that a subinterval on
    which f changes sign can be hard to find. On each published interval, f changes sign an even number of times, at 2
    roots only ``2/M`` apart.

    Each modified interval is already such a subinterval, around the left root, so the modified test problem does not
    test finding that subinterval.
    """

    number = (1, 99, 4, 2, 1)
    name = "(1.2)"
    param_names = ("M", "a", "b", "c_scale")
    source = FormulaSource(
        reference=(
            "Süli, E., Mayers, D. F. (2003). An Introduction to Numerical Analysis. Cambridge "
            "University Press, Cambridge. https://doi.org/10.1017/CBO9780511801181."
        ),
        location="(1.2)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, M: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c + 1.05``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        x = x + 1.05
        return 1 / 2 - 1 / (1 + M * abs(x - 1.05))

    def interval_bounds(self, M: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("M", "a", "b", "c_scale"),
                rows=(
                    (200.0, -0.01, 0.0, 0.01),
                    (2000.0, -0.001, 0.0, 0.001),
                    (20000.0, -0.0001, 0.0, 0.0001),
                    (200000.0, -1e-05, 0.0, 1e-05),
                    (2000000.0, -1e-06, 0.0, 1e-06),
                    (20000000.0, -1e-07, 0.0, 1e-07),
                    (2000000.0, -1e-05, 0.0, 1e-05),
                    (20000000.0, -1e-05, 0.0, 1e-05),
                ),
            ),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel
    test_cases = (
        FormulaTestCase.interval_bounds(
            params={"M": 200.0, "a": -0.01, "b": 0.0, "c_scale": 0.01}, expected=(-0.01, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 2000.0, "a": -0.001, "b": 0.0, "c_scale": 0.001}, expected=(-0.001, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 20000.0, "a": -0.0001, "b": 0.0, "c_scale": 0.0001}, expected=(-0.0001, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 200000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05}, expected=(-1e-05, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 2000000.0, "a": -1e-06, "b": 0.0, "c_scale": 1e-06}, expected=(-1e-06, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 20000000.0, "a": -1e-07, "b": 0.0, "c_scale": 1e-07}, expected=(-1e-07, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 2000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05}, expected=(-1e-05, 0.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"M": 20000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05}, expected=(-1e-05, 0.0)
        ),
        FormulaTestCase.value(
            params={"M": 200.0, "a": -0.01, "b": 0.0, "c_scale": 0.01}, x=-0.007, c=0.25, expected=0.15517241379310392
        ),
        FormulaTestCase.value(
            params={"M": 2000.0, "a": -0.001, "b": 0.0, "c_scale": 0.001},
            x=-0.0007,
            c=0.25,
            expected=0.1551724137930944,
        ),
        FormulaTestCase.value(
            params={"M": 20000.0, "a": -0.0001, "b": 0.0, "c_scale": 0.0001},
            x=-7e-05,
            c=0.25,
            expected=0.15517241379289376,
            atol=1e-11,
        ),
        FormulaTestCase.value(
            params={"M": 200000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05},
            x=-7e-06,
            c=0.25,
            expected=0.15517241379194327,
            atol=1e-10,
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": -1e-06, "b": 0.0, "c_scale": 1e-06},
            x=-7e-07,
            c=0.25,
            expected=0.15517241378243837,
            atol=1e-09,
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": -1e-07, "b": 0.0, "c_scale": 1e-07},
            x=-7e-08,
            c=0.25,
            expected=0.15517241389860917,
            atol=1e-08,
        ),
        FormulaTestCase.value(
            params={"M": 2000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05},
            x=-7e-06,
            c=0.25,
            expected=0.4499999999997561,
            atol=1e-11,
        ),
        FormulaTestCase.value(
            params={"M": 20000000.0, "a": -1e-05, "b": 0.0, "c_scale": 1e-05},
            x=-7e-06,
            c=0.25,
            expected=0.4947643979057324,
        ),
    )
