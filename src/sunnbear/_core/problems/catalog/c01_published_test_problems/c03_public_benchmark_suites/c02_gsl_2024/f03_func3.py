"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func3`` in the survey of published test problems. A change of the
formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class Gsl2024Func3(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``x^2 - 1e-8``; the formula's interval is ``[0, 1]``.

    Starting point 1; derivative given
    """

    number = (1, 3, 2, 3)
    name = "func3"
    param_names = ()
    source = FormulaSource(
        reference=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` "
            "(copyright Reid Priedhorsky, Brian Gough), "
            "https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite "
            "no source for their functions."
        ),
        location="func3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**2 - 1e-8

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=0.08999998999999999),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=0.002499989999999999),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
