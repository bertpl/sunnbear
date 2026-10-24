"""This module holds a formula of GSL (2024).

The formula comes from the row with the key ``func6`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Gsl2024Func6(Formula):
    """This formula comes from GSL (2024).

    The survey writes the source's function as ``(x - 1)^7``; the formula's interval is ``[0.9995, 1.0002]``.

    Starting point 0.9, run by `steffenson` only; derivative given

    With ``modified = 1``, the formula evaluates the published function at ``x + 1``, on the published interval shifted
    by -1, ``[-0.0005, 0.0002]``, which lies around 0.

    With ``modified = 1``, ``c`` shifts x as category 1 states, with ``c_scale`` the rounded width of the new interval.

    The published test function does not satisfy the benchmark suite inclusion conditions, because its interval is
    narrow around the root at 1: the ratio of the interval's largest bound to its width, about 1429, is above the
    conditions' limit of 100.
    """

    number = (1, 3, 2, 5)
    name = "func6"
    param_names = ("a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "GNU Scientific Library (GSL), release 2.8, files `roots/test_funcs.c` and `roots/test.c` "
            "(copyright Reid Priedhorsky, Brian Gough), "
            "https://cgit.git.savannah.gnu.org/cgit/gsl.git/tree/roots/?h=release-2-8. The files cite "
            "no source for their functions."
        ),
        location="func6",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x - c_scale*c + 1.0``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - c_scale * c
        if modified == 1:
            x = x + 1.0
        return (x - 1) ** 7

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.9995, 1.0002, 0.0007, 0.0),)),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((-0.0005, 0.0002, 0.0007, 1.0),)),
        )

    # a case with `atol=0.0` has an expected value so small that the default `atol`
    # would accept any value near 0, 0 among them
    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.9995, "b": 1.0002, "c_scale": 0.0007, "modified": 0.0},
            x=0.99971,
            c=0.0,
            expected=-1.7249876309005193e-25,
            atol=0.0,
        ),
        FormulaTestCase.value(
            params={"a": 0.9995, "b": 1.0002, "c_scale": 0.0007, "modified": 0.0},
            x=0.99971,
            c=0.25,
            expected=-4.700788051625088e-24,
            atol=0.0,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.9995, "b": 1.0002, "c_scale": 0.0007, "modified": 0.0}, expected=(0.9995, 1.0002)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": -0.0005, "b": 0.0002, "c_scale": 0.0007, "modified": 1.0}, expected=(-0.0005, 0.0002)
        ),
        FormulaTestCase.value(
            params={"a": -0.0005, "b": 0.0002, "c_scale": 0.0007, "modified": 1.0},
            x=-0.00029,
            c=0.25,
            expected=-4.700788051625088e-24,
        ),
    )
