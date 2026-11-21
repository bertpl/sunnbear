"""This module holds a formula of Kumar, Srivastav (2026).

The formula comes from the row with the key ``f2`` in the survey of published test problems. A change of the formula's
row in `data/literature_test_problems/sources/` needs a change of this module.
"""

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class KumarSrivastav2026F2(Formula):
    """This formula comes from Kumar, Srivastav (2026).

    The survey writes the source's function as ``x^3 + x - 1``; the formula's interval is ``[0, 1]``.

    Stated root `0.682328...`.
    """

    number = (1, 2, 19, 1)
    name = "f2"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Kumar, D., Srivastav, S. K. (2026). A randomized bracketing method for derivative-free "
            "root finding with uniform spacing contraction. Research Square preprint. "
            "https://doi.org/10.21203/rs.3.rs-10070193/v1. The article's Data Availability statement "
            "offers the authors' scripts from the corresponding author on request."
        ),
        location="f2",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**3 + x - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    test_cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.673),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.949875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
