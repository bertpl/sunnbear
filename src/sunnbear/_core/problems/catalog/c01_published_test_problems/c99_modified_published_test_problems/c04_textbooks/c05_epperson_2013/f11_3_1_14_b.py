"""This module holds formula f1.99.4.5.11, the modified version of the published formula f1.4.5.11.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.5.11 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedEpperson20133114B(Formula):
    """This formula is the modified version of formula f1.4.5.11, from Epperson (2013).

    The survey writes the source's function as ``1/(x - 1)``; the published interval is ``[0, 3]``.

    No root: a pole at `x = 1`. As 3.1-14(a).

    The formula returns 0 where ``x - c_scale*c`` equals 1, the 1 point at which the published function divides by 0;
    everywhere else it is the published function.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because it raises
    `ZeroDivisionError` at that point, where a solver's evaluation can land.
    """

    number = (1, 99, 4, 5, 11)
    name = "3.1-14(b)"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="3.1-14(b)",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, with 0 at the pole; category 1 states ``c_scale``."""
        x = x - 3.0 * c
        if x == 1:
            return 0.0
        else:
            return 1 / (x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-1.1764705882352942),
        FormulaTestCase.value(params={}, x=1.0, c=0.0, expected=0.0),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
