"""This formula is a line plus an odd power, ``s*x + (1 - s)*x^n + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_power, power_and_slope_recipes

# The lowest power ``n`` of the formula; every valid power is odd. With ``n = 1`` the function is the line ``x + c``
# for every ``s``.
LOWEST_POWER = 3


class LinearPlusOddPower(Formula):
    """`LinearPlusOddPower` is the polynomial ``s*x + (1 - s)*x^n + c`` with an odd power ``n``.

    At ``c = 0`` the function passes through ``(-1, -1)`` and ``(1, 1)``, and is odd-symmetric about its root at 0.

    ``s`` is the slope at ``x = 0``:

    - between 0 and 1, the function is increasing, and it flattens around 0 as ``s`` falls;
    - at 0, the function is the power ``x^n``;
    - below 0, the function has a local maximum left of 0 and a local minimum right of 0, and 3 roots in ``[-1, 1]``
      while ``abs(c)`` stays below the height of those extrema.

    ``c`` adds to the function value, so it moves the root away from 0: the root of ``x^n + c`` has multiplicity
    ``n`` only at ``c = 0``.
    """

    number = (2, 1, 3)
    name = "Linear plus odd power"
    param_names = ("n", "s")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, s: float) -> float:
        """Evaluate ``s*x + (1 - s)*x^n + c``."""
        return s * x + (1.0 - s) * x**n + c

    def interval_bounds(self, n: float, s: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every odd power with every slope."""
        return power_and_slope_recipes(LOWEST_POWER)

    def is_param_tuple_valid(self, n: float, s: float) -> bool:
        """Require ``n`` to be an odd integer of at least 3."""
        return is_valid_power(n, LOWEST_POWER)

    test_cases = (
        FormulaTestCase.value(params={"n": 3.0, "s": 0.5}, x=0.5, c=0.0, expected=0.3125),  # 0.25 + 0.5*0.125
        FormulaTestCase.value(params={"n": 3.0, "s": 0.5}, x=0.5, c=-0.1, expected=0.2125),  # exercises c
        FormulaTestCase.value(params={"n": 3.0, "s": 0.0}, x=0.5, c=0.0, expected=0.125),  # the power alone
        FormulaTestCase.value(params={"n": 5.0, "s": -1.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"n": 4.0, "s": 0.5}),  # even power
        FormulaTestCase.invalid(params={"n": 3.5, "s": 0.5}),  # power that is not an integer
        FormulaTestCase.invalid(params={"n": 1.0, "s": 0.5}),  # power below the lowest one
        FormulaTestCase.interval_bounds(params={"n": 3.0, "s": 0.5}, expected=(-1.0, 1.0)),
    )
