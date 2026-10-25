"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``§1.7`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Moler200417(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``x^7 - 7*x^6 + 21*x^5 - 35*x^4 + 35*x^3 - 21*x^2 + 7*x - 1``; the
    formula's interval is ``[0.988, 1.012]``.

    The expanded form of `(x - 1)^7`, which the book says was made with the Symbolic Toolbox. §1.7 plots it at `x =
    0.988:.0001:1.012` (Figure 1.9, "Is this a polynomial?") to show roundoff error: the plot is not smooth, with values
    of order `10^-14`, because of subtractive cancellation; evaluated as `(x-1).^7`, the plot is smooth. No root is
    sought.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``(x - 1)**7``, on the
    published interval, and ``c`` shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    The terms of the published form cancel, so that f is exactly 0 at many x-values across the interval, up to about
    0.01 from the root; ``(x - 1)**7`` has no terms that cancel.

    With ``modified = 1``, the modification changes what the test problem tests: the source plots f on the interval to
    show the roundoff error that the cancellation of its terms gives f (Figure 1.9), and ``(x - 1)**7`` has no such
    error.
    """

    number = (1, 4, 3, 2)
    name = "§1.7"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="§1.7",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, as ``(x - c_scale*c - 1)**7`` with ``modified = 1``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.024 * c
        if modified == 1:
            return (x - 1) ** 7
        else:
            return x**7 - 7 * x**6 + 21 * x**5 - 35 * x**4 + 35 * x**3 - 21 * x**2 + 7 * x - 1

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.988, 1.012)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel;
    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=0.9952, c=0.0, expected=-5.870683422720226e-17, atol=4e-13),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.9952, c=0.25, expected=-1.7138242687795553e-14, atol=4e-13),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(0.988, 1.012)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(0.988, 1.012)),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.9952, c=0.25, expected=-1.7138242687795553e-14, atol=0.0),
    )
