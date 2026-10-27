"""This module holds formula f1.99.4.5.21, the modified version of the published formula f1.4.5.21.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.4.5.21 may need a matching change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedEpperson2013Ex310(Formula):
    """This formula is the modified version of formula f1.4.5.21, from Epperson (2013).

    The survey writes the source's function as ``x^4 - x - 1``; the published interval is `[-2, 2]` (Fig. 3.11).

    Real roots 1.22074408460576 and -0.72449195900052, complex roots `-0.24812606280262 ± 1.03398206097597i`. Newton
    from `x0 = 1.25` and `x0 = -0.75`, then deflation (Ex. 3.10, Table 3.7); Durand–Kerner from complex starts (Ex.
    3.11, Table 3.8), and from the real starts 1, -1, 2, -2, where it fails (Ex. 3.14, Table 3.11).

    The formula changes the published interval ``[-2, 2]`` to ``[-2, 1]``: the upper bound moves left of the second
    root, near 1.22, so that the interval holds 1 of the 2 roots; ``c`` shifts x by the rule of category 1, with
    ``c_scale`` the rounded width of the new interval.

    The published test problem does not satisfy the benchmark suite inclusion conditions, because the published
    interval holds 2 roots, an even number, so that ``f(a)`` and ``f(b)`` have the same sign.
    """

    number = (1, 99, 4, 5, 21)
    name = "Ex. 3.10"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Epperson, J. F. (2013). An Introduction to Numerical Methods and Analysis, 2nd edition. "
            "John Wiley & Sons, Hoboken, NJ. ISBN 978-1-118-36759-9."
        ),
        location="Ex. 3.10, 3.11, 3.14",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``.

        Category 1 states the rule for ``c_scale``.
        """
        x = x - 3.0 * c
        return x**4 - x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-2.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=-1.1, c=0.25, expected=12.563506250000003),
        FormulaTestCase.interval_bounds(params={}, expected=(-2.0, 1.0)),
    )
