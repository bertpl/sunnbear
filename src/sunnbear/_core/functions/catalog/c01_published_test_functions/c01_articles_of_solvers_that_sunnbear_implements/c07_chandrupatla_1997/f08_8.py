"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``8`` in the survey of published test problems. The module generator,
`scripts/literature_test_problems/formula_modules.py`, does not write a formula with the parameter ``modified``, which
selects a modified version of a published test function.

A person therefore writes this module by hand, starting from the module that the generator writes for the formula when
the formula is absent from `MODIFIED_FORMULAS` in `scripts/literature_test_problems/modified_formulas.py`. A change of
the formula's row in `data/literature_test_problems/sources/` needs a matching change of this module.
"""

import math

from sunnbear._core.functions.core import Formula, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Chandrupatla19978(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``-3062*(1 - xi)*exp(-x)/(xi + (1 - xi)*exp(-x)) - 1013 + 1628/x``, with
    the parameters ``xi = 0.61489``; the formula's intervals are `[2E-4, 2]`; `[2E-4, 3]`; `[2E-4, 9]`; `[2E-4, 27]`;
    `[2E-4, 81]`.

    Printed zero: `x = 1.037536`.

    With ``modified = 1``, the formula evaluates the published function at ``x*exp(-c*ln(b/a))`` on the published
    interval: ``c`` scales x, so that the root moves by the factor ``(b/a)**c`` and never reaches 0. As ``c`` goes from
    0 to 1, the root moves by the interval's full width in log scale.

    The published test functions fail a benchmark suite's checks of its test functions, because each interval spans
    orders of magnitude next to the pole of ``1628/x`` at 0.

    The range of ``c`` in which ``f(a)`` keeps its sign and size is therefore narrower than the minimum width that the
    checks require.
    """

    number = (1, 1, 7, 8)
    name = "8"
    param_names = ("xi", "a", "b", "c_scale", "modified")
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, xi: float, a: float, b: float, c_scale: float, modified: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``, or, with ``modified = 1``, at ``x*exp(-c*ln(b/a))``.

        Category 1 states the rule for ``c_scale``.
        """
        if modified == 0:
            x = x - c_scale * c
        else:
            x = x * math.exp(-c * math.log(b / a))
        return -3062 * (1 - xi) * math.exp(-x) / (xi + (1 - xi) * math.exp(-x)) - 1013 + 1628 / x

    def interval_bounds(self, xi: float, a: float, b: float, c_scale: float, modified: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values, then those of the modified test functions."""
        return (
            ParamTable(
                names=("xi", "a", "b", "c_scale", "modified"),
                rows=(
                    (0.61489, 0.0002, 2.0, 2.0, 0.0),
                    (0.61489, 0.0002, 3.0, 3.0, 0.0),
                    (0.61489, 0.0002, 9.0, 9.0, 0.0),
                    (0.61489, 0.0002, 27.0, 27.0, 0.0),
                    (0.61489, 0.0002, 81.0, 81.0, 0.0),
                ),
            ),
            ParamTable(
                names=("xi", "a", "b", "c_scale", "modified"),
                rows=(
                    (0.61489, 0.0002, 2.0, 2.0, 1.0),
                    (0.61489, 0.0002, 3.0, 3.0, 1.0),
                    (0.61489, 0.0002, 9.0, 9.0, 1.0),
                    (0.61489, 0.0002, 27.0, 27.0, 1.0),
                    (0.61489, 0.0002, 81.0, 81.0, 1.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0, "c_scale": 2.0, "modified": 0.0},
            x=0.60014,
            c=0.0,
            expected=916.522638861195,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0, "c_scale": 2.0, "modified": 0.0},
            x=0.60014,
            c=0.25,
            expected=14136.757677926018,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 3.0, "c_scale": 3.0, "modified": 0.0},
            x=0.90014,
            c=0.0,
            expected=174.22250247527253,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 9.0, "c_scale": 9.0, "modified": 0.0},
            x=2.70014,
            c=0.0,
            expected=-533.729466491803,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 27.0, "c_scale": 27.0, "modified": 0.0},
            x=8.10014,
            c=0.0,
            expected=-812.597740310443,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 81.0, "c_scale": 81.0, "modified": 0.0},
            x=24.3001,
            c=0.0,
            expected=-946.0043909820606,
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0, "c_scale": 2.0, "modified": 0.0}, expected=(0.0002, 2.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 3.0, "c_scale": 3.0, "modified": 0.0}, expected=(0.0002, 3.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 9.0, "c_scale": 9.0, "modified": 0.0}, expected=(0.0002, 9.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 27.0, "c_scale": 27.0, "modified": 0.0}, expected=(0.0002, 27.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 81.0, "c_scale": 81.0, "modified": 0.0}, expected=(0.0002, 81.0)
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0, "c_scale": 2.0, "modified": 1.0},
            x=0.0502377,
            c=0.25,
            expected=321870.8552288529,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 3.0, "c_scale": 3.0, "modified": 1.0},
            x=0.0640744,
            c=0.25,
            expected=278997.32381392096,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 9.0, "c_scale": 9.0, "modified": 1.0},
            x=0.123868,
            c=0.25,
            expected=189238.842524578,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 27.0, "c_scale": 27.0, "modified": 1.0},
            x=0.239458,
            c=0.25,
            expected=128136.06406767729,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 81.0, "c_scale": 81.0, "modified": 1.0},
            x=0.462917,
            c=0.25,
            expected=86539.74096002016,
        ),
    )
