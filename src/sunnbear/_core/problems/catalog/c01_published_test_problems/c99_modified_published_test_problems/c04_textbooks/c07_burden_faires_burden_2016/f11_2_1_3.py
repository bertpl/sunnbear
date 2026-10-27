"""This module holds formula f1.99.4.7.11, the modified version of the published formula f1.4.7.11.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.7.11 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedBurdenFairesBurden2016213(Formula):
    """This formula is the modified version of formula f1.4.7.11, from Burden, Faires, Burden (2016).

    The survey writes the source's function as ``x^3 - 7*x^2 + 14*x - 6``; the published intervals are `[0, 1]`; `[1,
    3.2]`; `[3.2, 4]`.

    Bisection to `1E-2` on each interval (2.1-3); all zeros to `1E-5` by Newton with deflation (2.6-2).

    The formula holds only the test problem on ``[3.2, 4]``. The formula computes the published function in the
    equivalent form ``(x - 3)*((x - 2)**2 - 2)``, on that interval; ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the published interval.

    The published test problem on ``[3.2, 4]`` does not satisfy the benchmark suite inclusion conditions, because the
    conditions require bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint
    lands on an exact 0 of f.

    Near the root ``2 + sqrt(2)``, the terms of the published form cancel, so that f is exactly 0 at many x-values
    within about 1e-14 of the root.

    The equivalent form rounds only the square ``(x - 2)**2``: on the interval, ``x - 3`` and ``x - 2`` are exact, and so
    is the subtraction of 2 from the square near the root. No float64 x near the root makes the square round to exactly
    2, so f is exactly 0 at no x-value near the root.
    """

    number = (1, 99, 4, 7, 11)
    name = "2.1-3"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Burden, R. L., Faires, J. D., Burden, A. M. (2016). Numerical Analysis, 10th edition. "
            "Cengage Learning, Boston, MA. ISBN 978-1-305-25366-7. The copyright page gives © 2016 and "
            "the print year 2014."
        ),
        location="2.1-3; 2.6-2(h)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(y - 3)*((y - 2)**2 - 2)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.8 * c
        return (x - 3) * ((x - 2) ** 2 - 2)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (3.2, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(3.2, 4.0)),
        FormulaTestCase.value(params={}, x=3.44, c=0.25, expected=-0.11097600000000003),
    )
