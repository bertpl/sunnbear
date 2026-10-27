"""This module holds formula f1.99.4.3.2, the modified version of the published formula f1.4.3.2.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.3.2 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedMoler200417(Formula):
    """This formula is the modified version of formula f1.4.3.2, from Moler (2004).

    The survey writes the source's function as ``x^7 - 7*x^6 + 21*x^5 - 35*x^4 + 35*x^3 - 21*x^2 + 7*x - 1``; the
    published interval is ``[0.988, 1.012]``.

    The expanded form of `(x - 1)^7`, which the book says was made with the Symbolic Toolbox. §1.7 plots it at `x =
    0.988:.0001:1.012` (Figure 1.9, "Is this a polynomial?") to show roundoff error: the plot is not smooth, with values
    of order `10^-14`, because of subtractive cancellation; evaluated as `(x-1).^7`, the plot is smooth. No root is
    sought.

    The formula computes the published function in the equivalent form ``(x - 1)**7``, on the published interval;
    ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    The terms of the published form cancel, so that f is exactly 0 at many x-values across the interval, up to about
    0.01 from the root; ``(x - 1)**7`` has no terms that cancel.

    The modification changes what the test problem tests: the source plots f on the interval to show the roundoff error
    of f from the cancellation of the published form's terms (Figure 1.9), and ``(x - 1)**7`` has no such error.
    """

    number = (1, 99, 4, 3, 2)
    name = "§1.7"
    param_names = ()
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
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, as ``(x - c_scale*c - 1)**7``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 0.024 * c
        return (x - 1) ** 7

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.988, 1.012)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    # a case with a positive `atol` lies where float64 cannot evaluate the function to the
    # default tolerance, because the function is ill-conditioned there or its terms cancel;
    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(0.988, 1.012)),
        FormulaTestCase.value(params={}, x=0.9952, c=0.25, expected=-1.7138242687795553e-14, atol=0.0),
    )
