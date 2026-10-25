"""This module holds a formula of Moler (2004).

The formula comes from the row with the key ``Ex. 4.3`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Moler2004Ex43(Formula):
    """This formula comes from Moler (2004).

    The survey writes the source's function as ``816*x^3 - 3835*x^2 + 6000*x - 3125``; the formula's interval is ``[1,
    2]``.

    The book calls `p(x)` a cubic with 3 closely spaced real roots. Ex. 4.3 asks for its exact roots; plots it for `1.43
    <= x <= 1.71`; runs Newton from `x0 = 1.5`, the secant method from `x0 = 1, x1 = 2`, and bisection on `[1, 2]`; and
    asks what `fzerotx(p,[1,2])` returns, and why.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``(17*x - 25)*(16*x -
    25)*(3*x - 5)``, on the published interval, and ``c`` shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near each of the roots ``25/17``, ``25/16`` and ``5/3``, the terms of the published form cancel, so that f is
    exactly 0 at many x-values within about 3e-13 of the root; ``(17*x - 25)*(16*x - 25)*(3*x - 5)`` has no terms that
    cancel.
    """

    number = (1, 4, 3, 14)
    name = "Ex. 4.3"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Moler, C. B. (2004). Numerical Computing with MATLAB. SIAM, Philadelphia (print edition); "
            "The MathWorks, Natick, MA (electronic edition). ISBN 0-89871-560-1. The author's web "
            "edition, 1 PDF per chapter: https://www.mathworks.com/moler/chapters.html; chapter 4: "
            "https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/moler/zeros.pdf."
        ),
        location="Ex. 4.3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        With ``modified = 1``, evaluate it as ``(17*y - 25)*(16*y - 25)*(3*y - 5)``, with ``y = x - c_scale*c``.
        Category 1 states the rule for ``c_scale``.
        """
        x = x - 1.0 * c
        if modified == 1:
            return (17 * x - 25) * (16 * x - 25) * (3 * x - 5)
        else:
            return 816 * x**3 - 3835 * x**2 + 6000 * x - 3125

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=1.3, c=0.0, expected=-13.397999999999993),
        FormulaTestCase.value(params={"modified": 0.0}, x=1.3, c=0.25, expected=-108.46549999999998),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(1.0, 2.0)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(1.0, 2.0)),
        FormulaTestCase.value(params={"modified": 1.0}, x=1.3, c=0.25, expected=-108.46549999999998),
    )
