"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-3(h); 3.2-5(e); 3.3-3(g)`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Epperson2013313H(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``x^2 - sin(x)``; the formula's interval is ``[0, pi]``.

    Bisection to `1E-6`; Newton from `x0 = 1/2`.
    """

    number = (1, 4, 5, 8)
    name = "3.1-3(h)"
    params = ()
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="3.1-3(h); 3.2-5(e); 3.3-3(g)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.14 * c
        return x**2 - math.sin(x)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.141592653589793)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.942478, c=0.0, expected=0.07924766624610098),
        FormulaTestCase.value(params={}, x=0.942478, c=0.25, expected=-0.1320285948907636),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.141592653589793)),
    )
