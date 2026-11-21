"""This module holds a formula of Epperson (2013).

The formula comes from the row with the key ``3.1-14(b)`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Epperson20133114B(Formula):
    """This formula comes from Epperson (2013).

    The survey writes the source's function as ``1/(x - 1)``; the formula's interval is ``[0, 3]``.

    No root: a pole at `x = 1`. As 3.1-14(a).
    """

    number = (1, 4, 5, 11)
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
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 3.0 * c
        return 1 / (x - 1)

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 3.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.9, c=0.0, expected=-10.000000000000002),
        FormulaTestCase.value(params={}, x=0.9, c=0.25, expected=-1.1764705882352942),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 3.0)),
    )
