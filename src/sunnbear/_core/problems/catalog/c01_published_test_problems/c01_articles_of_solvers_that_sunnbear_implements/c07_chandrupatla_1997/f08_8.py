"""This module holds a formula of Chandrupatla (1997).

The formula comes from the row with the key ``8`` in the survey of published test problems.
"""

import math

from sunnbear._core.problems.core import Formula, FormulaParam, FormulaSource, FormulaTestCase, ParamRecipe, ParamTable


class Chandrupatla19978(Formula):
    """This formula comes from Chandrupatla (1997).

    The survey writes the source's function as ``-3062*(1 - xi)*exp(-x)/(xi + (1 - xi)*exp(-x)) - 1013 + 1628/x``, with
    the parameters ``xi = 0.61489``; the formula's intervals are `[2E-4, 2]`; `[2E-4, 3]`; `[2E-4, 9]`; `[2E-4, 27]`;
    `[2E-4, 81]`.

    Printed zero: `x = 1.037536`.
    """

    number = (1, 1, 7, 8)
    name = "8"
    params = (
        FormulaParam("xi"),
        FormulaParam("a"),
        FormulaParam("b"),
        FormulaParam("c_scale"),
    )
    source = FormulaSource(
        reference=(
            "Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the "
            "zero of a nonlinear function without using derivatives. Advances in Engineering Software "
            "28(3), 145–149. https://doi.org/10.1016/S0965-9978(96)00051-8."
        ),
        location="8",
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, xi: float, a: float, b: float, c_scale: float) -> float:
        """Evaluate the published function at ``x - c_scale*c``; category 1 states the rule for ``c_scale``."""
        x = x - c_scale * c
        return -3062 * (1 - xi) * math.exp(-x) / (xi + (1 - xi) * math.exp(-x)) - 1013 + 1628 / x

    def interval_bounds(self, xi: float, a: float, b: float, c_scale: float) -> tuple[float, float]:
        """Return the interval of the tuple, its parameters ``a`` and ``b``."""
        return (a, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the published parameter values."""
        return (
            ParamTable(
                names=("xi", "a", "b", "c_scale"),
                rows=(
                    (0.61489, 0.0002, 2.0, 2.0),
                    (0.61489, 0.0002, 3.0, 3.0),
                    (0.61489, 0.0002, 9.0, 9.0),
                    (0.61489, 0.0002, 27.0, 27.0),
                    (0.61489, 0.0002, 81.0, 81.0),
                ),
            ),
        )

    test_cases = (
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0, "c_scale": 2.0}, x=0.60014, c=0.0, expected=916.522638861195
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0, "c_scale": 2.0},
            x=0.60014,
            c=0.25,
            expected=14136.757677926018,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 3.0, "c_scale": 3.0}, x=0.90014, c=0.0, expected=174.22250247527253
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 9.0, "c_scale": 9.0}, x=2.70014, c=0.0, expected=-533.729466491803
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 27.0, "c_scale": 27.0},
            x=8.10014,
            c=0.0,
            expected=-812.597740310443,
        ),
        FormulaTestCase.value(
            params={"xi": 0.61489, "a": 0.0002, "b": 81.0, "c_scale": 81.0},
            x=24.3001,
            c=0.0,
            expected=-946.0043909820606,
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 2.0, "c_scale": 2.0}, expected=(0.0002, 2.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 3.0, "c_scale": 3.0}, expected=(0.0002, 3.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 9.0, "c_scale": 9.0}, expected=(0.0002, 9.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 27.0, "c_scale": 27.0}, expected=(0.0002, 27.0)
        ),
        FormulaTestCase.interval_bounds(
            params={"xi": 0.61489, "a": 0.0002, "b": 81.0, "c_scale": 81.0}, expected=(0.0002, 81.0)
        ),
    )
