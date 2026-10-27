"""This module holds formula f1.99.1.8.1, the modified version of the published formula f1.1.8.1.

A person writes this module: the module generator, `scripts/literature_test_problems/formula_modules.py`, writes only
the published formulas of category 1. A change of formula f1.1.8.1 may need a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe


class ModifiedFord19971(Formula):
    """This formula is the modified version of formula f1.1.8.1, from Ford (1997).

    The survey writes the source's function as ``sin(0.01/x) - 0.01``; the published intervals are `[0.5, 2]`;
    `[0.2, 6]`; `[0.004, 200]`.

    Printed root: `x* = 0.99998333286109`.

    The formula holds only the test problem on ``[0.004, 200]``. It evaluates the published function at
    ``x*exp(-c*ln(b/a))`` on the published interval ``[a, b]``: ``c`` scales x, so that the root moves by the factor
    ``(b/a)**c`` and never reaches 0. As ``c`` goes from 0 to 1, the root moves by the interval's full width in log
    scale.

    The published test problem on ``[0.004, 200]`` does not satisfy the benchmark suite inclusion conditions, because
    the interval spans orders of magnitude next to the singularity of ``sin(0.01/x)`` at 0.

    A shift along x by ``c_scale*c`` takes ``a`` to the pole at 0 for a small ``c``, so the range of ``c`` in which
    ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0`` is narrower than the minimum width that the
    conditions require.
    """

    number = (1, 99, 1, 8, 1)
    name = "1"
    param_names = ()
    source = FormulaSource(
        reference=(
            "Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear "
            "equations. Scientia Iranica 4(1&2), 28–34. The article has no working DOI: the journal's "
            "page, https://scientiairanica.sharif.edu/article_21758.html, lists "
            "10.24200/sci.2020.21758, which doi.org does not resolve. An earlier version is the "
            "University of Essex technical report CSM-257 (1995)."
        ),
        location="1",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float) -> float:
        """Evaluate the published function at ``x*exp(-c*ln(b/a))``, with ``[a, b]`` the published interval."""
        x = x * math.exp(-c * math.log(200.0 / 0.004))
        return math.sin(0.01 / x) - 0.01

    def interval_bounds(self) -> tuple[float, float]:
        """Return the formula's interval."""
        return (0.004, 200.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return no recipe, since the modified function has no parameters."""
        return ()

    test_cases = (FormulaTestCase.value(params={}, x=2.63902, c=0.25, expected=0.046632716833441626),)
