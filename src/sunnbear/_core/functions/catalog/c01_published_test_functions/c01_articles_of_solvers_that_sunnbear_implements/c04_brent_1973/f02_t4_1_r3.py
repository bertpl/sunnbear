"""This module holds the formula of T4.1 r3 in Brent (1973).

A script generates this module from the survey of published test problems: to change the formula, change its source file
in `data/literature_test_problems/sources/` and run `uv run python -m scripts.literature_test_problems.formula_modules
1973_brent_book`, never this file.
"""

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe

# SURVEY_FIELDS_HASH is a hash of this formula's survey fields; the tests recompute it from the
# survey, so that a test fails when the survey changes and this module is not regenerated.
SURVEY_FIELDS_HASH = "9eb9fc0a4deebf3c"


class Brent1973T41R3(Formula):
    """This formula evaluates the published function at ``x - (b - a)*c``, where ``[a, b]`` is its interval.

    The source prints ``x^19``; the formula's interval is `[-1.0, +4.0]` with `t = 1E-20`.
    """

    number = (1, 1, 4, 2)
    name = "T4.1 r3"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall, "
            "Englewood Cliffs, NJ. ISBN 0-13-022335-2. Author's scan: "
            "https://maths-people.anu.edu.au/~brent/pub/pub011.html. Erratum: Brent, R. P. (1975). "
            "Table Errata 520. Mathematics of Computation, p. 1166."
        ),
        location="T4.1 r3",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x - (b - a)*c``, where ``[a, b]`` is the formula's interval."""
        x = x - 5.0 * c
        return x**19

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (-1.0, 4.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the published function has no parameters."""
        return ()

    cases = (
        FormulaTestCase.value(params={}, x=0.5, c=0.0, expected=1.9073486328125e-06),
        FormulaTestCase.value(params={}, x=0.5, c=0.25, expected=-0.004228282585245324),
        FormulaTestCase.interval_bounds(params={}, expected=(-1.0, 4.0)),
    )
