"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``f4`` in the survey of published test problems. The survey gives this
function as 1 expression that the module generator, `scripts/literature_test_problems/formula_modules.py`, cannot
translate: an expression with the stated root ``x*`` as a parameter. A person therefore writes this module, and a change
of the formula's row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class KumarSrivastav2026F4(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``(x - x*)^3 + 0.05*(x - x*)``, with the parameters ``x* = 0.6``; the
    formula's interval is ``[0, 1]``.

    The formula's parameter ``x_star`` is the source's ``x*``, the stated root.
    """

    number = (1, 2, 19, 3)
    name = "f4"
    param_names = ("x_star",)
    source = FormulaSource(
        reference=(
            "Kumar, D., Srivastav, S. K. (2026). A randomized bracketing method for derivative-free "
            "root finding with uniform spacing contraction. Research Square preprint. "
            "https://doi.org/10.21203/rs.3.rs-10070193/v1. The article's Data Availability statement "
            "offers the authors' scripts from the corresponding author on request."
        ),
        location="f4",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, x_star: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return (x - x_star) ** 3 + 0.05 * (x - x_star)

    def interval_bounds(self, x_star: float) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (ParamTable(names=("x_star",), rows=((0.6,),)),)

    test_cases = (
        FormulaTestCase.value(params={"x_star": 0.6}, x=0.3, c=0.0, expected=-0.041999999999999996),
        FormulaTestCase.value(params={"x_star": 0.6}, x=0.3, c=0.25, expected=-0.193875),
        FormulaTestCase.interval_bounds(params={"x_star": 0.6}, expected=(0.0, 1.0)),
    )
