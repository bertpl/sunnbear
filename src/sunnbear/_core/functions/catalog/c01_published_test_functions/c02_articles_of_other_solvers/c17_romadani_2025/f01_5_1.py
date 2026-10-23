"""This module holds a formula of Romadani (2025).

The formula comes from the row with the key ``5.1`` in the survey of published test problems. A script generates this
module from that survey: to change the formula, change its source file in `data/literature_test_problems/sources/` and
run `uv run python -m scripts.literature_test_problems.formula_modules 2025_romadani_python_implementations`; do not
edit this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "47367cc9f706b680"


class Romadani202551(Formula):
    """This formula comes from Romadani (2025).

    The survey writes the source's function as ``x^7 - 2*x^6 + 4*x^5 - 1``; the formula's interval is ``[0, 1]``.

    Eq. (8). Stated root `0.800631154473`.
    """

    number = (1, 2, 17, 1)
    name = "5.1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Romadani, M. N. H. (2025). From Theory to Code: Transforming Classical Root-Finding "
            "Methods into Efficient Python Implementations. ICCK Journal of Applied Mathematics 1(3), "
            "154–189. https://doi.org/10.62762/jam.2025.840767."
        ),
        location="5.1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - 1.0 * c
        return x**7 - 2 * x**6 + 4 * x**5 - 1

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=0.3, c=0.0, expected=-0.9915193),
        FormulaTestCase.value(params={}, x=0.3, c=0.25, expected=-0.99999878046875),
        FormulaTestCase.interval_bounds(params={}, expected=(0.0, 1.0)),
    )
