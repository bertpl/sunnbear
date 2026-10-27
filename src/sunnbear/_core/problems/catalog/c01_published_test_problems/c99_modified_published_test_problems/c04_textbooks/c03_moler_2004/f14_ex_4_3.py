"""This module holds formula f1.99.4.3.14, the modified version of the published formula f1.4.3.14.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.3.14 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedMoler2004Ex43(Formula):
    """This formula is the modified version of formula f1.4.3.14, from Moler (2004).

    The survey writes the source's function as ``816*x^3 - 3835*x^2 + 6000*x - 3125``; the published interval is ``[1,
    2]``.

    The book calls `p(x)` a cubic with 3 closely spaced real roots. Ex. 4.3 asks for its exact roots; plots it for `1.43
    <= x <= 1.71`; runs Newton from `x0 = 1.5`, the secant method from `x0 = 1, x1 = 2`, and bisection on `[1, 2]`; and
    asks what `fzerotx(p,[1,2])` returns, and why.

    The formula computes the published function in the equivalent form ``(17*x - 25)*(16*x - 25)*(3*x - 5)``, on the
    published interval; ``c`` shifts x by the rule of category 1, with ``c_scale`` the rounded width of the published
    interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the conditions require
    bisection to spend a fixed number of evaluations, and bisection stops early where a midpoint lands on an exact 0 of
    f.

    Near each of the roots ``25/17``, ``25/16`` and ``5/3``, the terms of the published form cancel, so that f is
    exactly 0 at many x-values within about 3e-13 of the root; ``(17*x - 25)*(16*x - 25)*(3*x - 5)`` has no terms that
    cancel.
    """

    number = (1, 99, 4, 3, 14)
    name = "Ex. 4.3"
    param_names = ()
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
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``y = x - c_scale*c``, as ``(17*y - 25)*(16*y - 25)*(3*y - 5)``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 1.0 * c
        return (17 * x - 25) * (16 * x - 25) * (3 * x - 5)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (1.0, 2.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.interval_bounds(params={}, expected=(1.0, 2.0)),
        FormulaTestCase.value(params={}, x=1.3, c=0.25, expected=-108.46549999999998),
    )
