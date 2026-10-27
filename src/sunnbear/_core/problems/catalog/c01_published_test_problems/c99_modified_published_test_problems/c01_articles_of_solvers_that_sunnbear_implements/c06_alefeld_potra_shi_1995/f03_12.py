"""This module holds formula f1.99.1.6.3, the modified version of the published formula f1.1.6.3.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.6.3 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class ModifiedAlefeldPotraShi199512(Formula):
    """This formula is the modified version of formula f1.1.6.3, from Alefeld, Potra, Shi (1995).

    The survey writes the source's function as ``x^(1/n) - n^(1/n)``, with the parameters ``n = 2(1)6, 7(2)33``; the
    published interval is ``[1, 100]``.

    Driver problem 25.

    The formula holds only the test problems with ``n = 27`` and ``n = 31``. The formula computes the published function
    in the equivalent form ``n**(1/n) * expm1(log(x/n)/n)``, on the published interval; ``c`` shifts x by the rule of
    category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problems with ``n = 27`` and ``n = 31`` do not satisfy the benchmark suite inclusion conditions,
    because the conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a
    midpoint lands on an exact 0 of f.

    Near the root, ``x = n``, the 2 terms of the published form cancel, so that f is exactly 0 at many x-values within
    about 1e-13 of the root. Of the published values of ``n``, only for ``n = 27`` and ``n = 31`` does bisection land on
    one of these x-values. ``expm1(log(x/n)/n)`` computes ``(x/n)**(1/n) - 1`` without the subtraction.
    """

    number = (1, 99, 1, 6, 3)
    name = "12"
    param_names = ("n",)
    source = FormulaSource(
        reference=(
            "Alefeld, G. E., Potra, F. A., Shi, Y. (1995). Algorithm 748: enclosing zeros of continuous"
            " functions. ACM Transactions on Mathematical Software 21(3), 327–344. "
            "https://doi.org/10.1145/210089.210111. The authors' code is CALGO 748: "
            "https://www.netlib.org/toms/748."
        ),
        location="12",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``n**(1/n) * expm1(log(y/n)/n)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 99.0 * c
        return n ** (1 / n) * math.expm1(math.log(x / n) / n)

    def interval_bounds(self, n: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 100.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the parameter values of the modified test problems."""
        return (
            ParamTable(
                names=("n",),
                rows=(
                    (27.0,),
                    (31.0,),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.interval_bounds(params={"n": 27.0}, expected=(1.0, 100.0)),
        FormulaTestCase.value(params={"n": 27.0}, x=30.7, c=0.25, expected=-0.061549203181192384),
        FormulaTestCase.interval_bounds(params={"n": 31.0}, expected=(1.0, 100.0)),
        FormulaTestCase.value(params={"n": 31.0}, x=30.7, c=0.25, expected=-0.05792643762161267),
    )
