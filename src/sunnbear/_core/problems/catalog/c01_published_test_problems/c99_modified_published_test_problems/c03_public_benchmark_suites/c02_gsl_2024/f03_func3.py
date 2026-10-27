"""This module holds formula f1.99.3.2.3, the modified version of the published formula f1.3.2.3.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.3.2.3 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedGsl2024Func3(Formula):
    """This formula is the modified version of formula f1.3.2.3, from GSL (2024).

    The survey writes the source's function as ``x^2 - 1e-8``; the published interval is ``[0, 1]``.

    Starting point 1; derivative given

    The formula keeps the published interval, evaluates the published function at x without shifting x, and adds ``c``
    to the function's value.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because its roots ``-1e-4``
    and ``1e-4`` lie ``1e-4`` from ``a = 0``: a shift along x by more than ``1e-4``, in either direction, changes the
    sign of ``f(a)``.

    The modification changes what the test problem tests: the published test problem has its root, ``1e-4``, close to
    the bound ``a = 0`` of an interval of width 1.

    Adding ``c`` moves the root to ``sqrt(1e-8 - c)``, so that the root stays close to ``a`` only for ``c`` near 0; for
    ``c = -0.25``, the root lies near 0.5.
    """

    number = (1, 99, 3, 2, 3)
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
        """Evaluate the published function at ``x``, and add ``c``."""
        return x**2 - 1e-8 + c

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=0.33999999),
        FormulaTestCase.value(params={}, x=0.0, c=-0.25, expected=-0.25000001),
    )
