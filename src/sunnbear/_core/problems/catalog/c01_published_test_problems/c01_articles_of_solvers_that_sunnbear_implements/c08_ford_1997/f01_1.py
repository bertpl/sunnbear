"""This module holds a formula of Ford (1997).

The formula comes from the row with the key ``1`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test problem.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Ford19971(Formula):
    """This formula comes from Ford (1997).

    The survey writes the source's function as ``sin(0.01/x) - 0.01``; the formula's intervals are `[0.5, 2]`; `[0.2,
    6]`; `[0.004, 200]`.

    Printed root: `x* = 0.99998333286109`.

    With ``modified = 1``, the formula evaluates the published function at ``x*exp(-c*ln(b/a))`` on the published
    interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c`` and never reaches 0. As ``c`` goes from
    0 to 1, the root moves by the interval's full width in log scale.

    The published test problem on ``[0.004, 200]`` does not satisfy the benchmark suite inclusion conditions, because
    the interval spans orders of magnitude next to the singularity of ``sin(0.01/x)`` at 0.

    A shift along x by ``c_scale*c`` takes ``a`` to the pole at 0 for a small ``c``, so the range of ``c`` in which
    ``f(a)`` keeps its sign and at least a tenth of its value at ``c = 0`` is narrower than the minimum width that the
    conditions require.
    """

    number = (1, 1, 8, 1)
    name = "1"
    param_names = ("a", "b", "c_scale", "modified")
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
    def parametrized_fun(x: float, c: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x*exp(-c*ln(b/a))``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - c_scale * c
        else:
            x = x * math.exp(-c * math.log(b / a))
        return math.sin(0.01 / x) - 0.01

    def interval_bounds(self, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test problems."""
        return (
            ParamTable(
                names=("a", "b", "c_scale", "modified"),
                rows=(
                    (0.5, 2.0, 1.5, 0.0),
                    (0.2, 6.0, 5.8, 0.0),
                    (0.004, 200.0, 200.0, 0.0),
                ),
            ),
            ParamTable(names=("a", "b", "c_scale", "modified"), rows=((0.004, 200.0, 200.0, 1.0),)),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"a": 0.5, "b": 2.0, "c_scale": 1.5, "modified": 0.0}, x=0.95, c=0.0, expected=0.0005261213987539786
        ),
        FormulaTestCase.value(
            params={"a": 0.5, "b": 2.0, "c_scale": 1.5, "modified": 0.0}, x=0.95, c=0.25, expected=0.00739042767277413
        ),
        FormulaTestCase.value(
            params={"a": 0.2, "b": 6.0, "c_scale": 5.8, "modified": 0.0}, x=1.94, c=0.0, expected=-0.004845383651434474
        ),
        FormulaTestCase.value(
            params={"a": 0.004, "b": 200.0, "c_scale": 200.0, "modified": 0.0},
            x=60.0028,
            c=0.0,
            expected=-0.009833341111519662,
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.5, "b": 2.0, "c_scale": 1.5, "modified": 0.0}, expected=(0.5, 2.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.2, "b": 6.0, "c_scale": 5.8, "modified": 0.0}, expected=(0.2, 6.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"a": 0.004, "b": 200.0, "c_scale": 200.0, "modified": 0.0}, expected=(0.004, 200.0)
        ),
        FormulaTestCase.value(
            params={"a": 0.004, "b": 200.0, "c_scale": 200.0, "modified": 1.0},
            x=2.63902,
            c=0.25,
            expected=0.046632716833441626,
        ),
    )
