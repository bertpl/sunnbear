"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func3`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Gsl2024Func3(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``x^2 - 1e-8``; the formula's interval is ``[0, 1]``.

    Starting point 1; derivative given

    With ``modified = 1``, the formula keeps the published interval, evaluates the published function at x without
    shifting x, and adds ``c`` to the function's value.

    The published test function does not satisfy the benchmark suite inclusion conditions, because its roots ``-1e-4``
    and ``1e-4`` lie ``1e-4`` from ``a = 0``: a shift along x by more than ``1e-4``, in either direction, changes the
    sign of ``f(a)``.
    """

    number = (1, 3, 2, 3)
    name = "func3"
    param_names = ("modified",)
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
    def parametrized_fun(x: float, c: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x`` and add ``c``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - 1.0 * c
            f_offset = 0.0
        else:
            f_offset = c
        return x**2 - 1e-8 + f_offset

    def interval_bounds(self, modified: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published test function, then its modified version."""
        return (
            ParamTable(names=("modified",), rows=((0.0,),)),
            ParamTable(names=("modified",), rows=((1.0,),)),
        )

    test_cases = (
        FormulaTestCase.value(params={"modified": 0.0}, x=0.3, c=0.0, expected=0.08999998999999999),
        FormulaTestCase.value(params={"modified": 0.0}, x=0.3, c=0.25, expected=0.002499989999999999),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.3, c=0.25, expected=0.33999999),
        FormulaTestCase.value(params={"modified": 1.0}, x=0.0, c=-0.25, expected=-0.25000001),
        FormulaTestCase.interval_bounds(params={"modified": 0.0}, expected=(0.0, 1.0)),
    )
