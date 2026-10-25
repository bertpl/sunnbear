"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``§3.11.4, Fig. 3.12`` in the survey of published test problems. The module
generator, `scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter
``modified``, which selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Epperson20133114(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^5 - (5/2)*x^4 + (5/2)*x^3 - (5/4)*x^2 + (5/16)*x - 1/32``; the
    formula's interval is ``[0.45, 0.55]``.

    Printed also as `(x - 1/2)^5`. Evaluated in floating point at 8000 points of the interval, its values form a band
    around 0.

    With ``modified = 1``, the formula computes the published function in the equivalent form ``(x - 0.5)**5``, on the
    published interval, and ``c`` shifts x as category 1 states.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near the root, the terms of the published form cancel, so that f is exactly 0 at many x-values within about 7e-4 of
    the root; ``(x - 0.5)**5`` has no terms that cancel.

    With ``modified = 1``, the modification changes what the test problem tests: the source evaluates f at 8000 points
    of the interval to show that near the multiple root the values of f form a band around 0, inside which a
    root-finding method's iterations stop early (Figure 3.12), and ``(x - 0.5)**5`` has no such band.
    """

    number = (1, 4, 5, 22)
    name = "§3.11.4"
    param_names = ("modified",)
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="§3.11.4, Fig. 3.12",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, as ``(x - c_scale*c - 0.5)**5`` with ``modified = 1``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.1 * c
        if modified == 1:
            return (x - 0.5) ** 5
        else:
            return x**5 - (5 / 2) * x**4 + (5 / 2) * x**3 - (5 / 4) * x**2 + (5 / 16) * x - 1 / 32

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.45, 0.55)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problem."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=0.48, c=0.0, expected=-3.200000000000014e-09),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.48, c=0.25, expected=-1.8452812500000082e-07),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(0.45, 0.55)),
        FormulaTestCase.interval_bounds(params={"modified": 1.0}, expected=(0.45, 0.55)),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.48, c=0.25, expected=-1.8452812500000082e-07),
    )
