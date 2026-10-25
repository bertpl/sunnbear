"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.11-25`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Epperson201331125(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``(x - 1)^5``; the formula's interval is ``[0.998, 1.002]``.

    Evaluated at 400 points in 3 forms: `(x - 1)^5`, `x^5 - 5*x^4 + 10*x^3 - 10*x^2 + 5*x - 1` and `-1 + x*(5 + x*(-10 +
    x*(10 + x*(-5 + x))))`.

    With ``modified = 1``, the formula evaluates the published function at ``x + 1``, on the published interval shifted
    by -1, ``[-0.002, 0.002]``, which lies around 0.

    With ``modified = 2``, the formula computes the function of ``modified = 1`` in the equivalent form ``x**5``, on
    the same interval.

    With ``modified = 1`` or ``2``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new
    interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because its interval is
    narrow around the root at 1: the ratio of the interval's largest bound to its width, about 250, is above the
    conditions' limit of 100.

    The test problem with ``modified = 1`` does not satisfy the conditions either, because they require bisection to
    spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of f.

    With ``modified = 1``, adding 1 to x rounds x to the spacing of the floats near 1, about 2.2e-16, so that f is
    exactly 0 where ``abs(x)`` is below about 1.1e-16; ``x**5`` adds nothing to x, so it does not round x.
    """

    number = (1, 4, 5, 23)
    name = "3.11-25"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="3.11-25",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x - c_scale*c + 1.0``.

        With ``modified = 2``, evaluate the function of ``modified = 1`` as ``(x - c_scale*c)**5``. Category 1 states
        the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 2:
            return x**5
        else:
            if modified == 1:
                x = x + 1.0
            return (x - 1) ** 5

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.998, 1.002, 0.004, 0.0),)),
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (-0.002, 0.002, 0.004, 1.0),
                    (-0.002, 0.002, 0.004, 2.0),
                ),
            ),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.998, "b": 1.002, "c_scale": 0.004, "modified": 0.0},
            x=0.9992,
            c=0.0,
            expected=-3.276800000000469e-16,
            atol=0.0,
        ),
        FormulaTestCase.value(
            params={"a": 0.998, "b": 1.002, "c_scale": 0.004, "modified": 0.0},
            x=0.9992,
            c=0.25,
            expected=-1.8895680000001248e-14,
            atol=0.0,
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
            expected=-1.8895680000001248e-14,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -0.002, "b": 0.002, "c_scale": 0.004, "modified": 2.0}, expected=(-0.002, 0.002)
        ),
        FormulaTestCase.value(
            params={"a": -0.002, "b": 0.002, "c_scale": 0.004, "modified": 2.0},
            x=-0.0008,
            c=0.25,
            expected=-1.889568e-14,
            atol=0.0,
        ),
    )
