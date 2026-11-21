"""This module holds a formula of Chapra, Canale (2015).

The formula comes from the row with the key ``Prob. 5.8`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ChapraCanale2015Prob58(Formula):
    """This formula comes from Chapra, Canale (2015).

    The survey writes the source's function as ``x^2 - 18``; the formula's interval is ``[4, 5]``.

    The problem asks for the positive square root of 18 by false position to `es = 0.5%`; it prints no function.
    """

    number = (1, 4, 6, 17)
    name = "Prob. 5.8"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Chapra, S. C., Canale, R. P. (2015). Numerical Methods for Engineers, 7th edition. "
            "McGraw-Hill Education, New York, NY. ISBN 978-0-07-339792-4. The 8th edition appeared in "
            "2021."
        ),
        location="Prob. 5.8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - 18

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (4.0, 5.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=4.3, c=0.0, expected=0.4899999999999985),
        FormulaTestCase.value(params={}, x=4.3, c=0.25, expected=-1.5975000000000015),
        FormulaTestCase.interval_bounds(params={}, expected=(4.0, 5.0)),
    )
