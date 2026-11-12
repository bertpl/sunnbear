"""This formula is a line plus the mean of the odd powers from 3 to ``n``, ``s*x + (1 - s)*O_n(x) + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_power, power_and_slope_recipes

# The lowest highest-power ``n`` of the formula, which gives a sum of 2 terms; every valid ``n`` is odd. With
# ``n = 3`` the function is `LinearPlusOddPower`'s.
LOWEST_POWER = 5


class LinearPlusSumOfOddPowers(Formula):
    """`LinearPlusSumOfOddPowers` is the polynomial ``s*x + (1 - s)*O_n(x) + c`` with an odd highest power ``n``.

    ``O_n(x) = (x^3 + x^5 + ... + x^n)/k`` is the mean of the ``k = (n - 1)/2`` odd powers from 3 to ``n``. Dividing
    by ``k`` makes the function pass through ``(-1, -1)`` and ``(1, 1)`` at ``c = 0``, for every ``n`` and ``s``.

    - ``s`` is the slope at ``x = 0``, as in `LinearPlusOddPower`.
    - ``n`` adds higher powers, which steepen the function toward the bounds. The term ``x^3`` dominates around 0
      for every ``n``, where a single high power is much flatter.

    ``c`` adds to the function value.
    """

    number = (2, 1, 5)
    name = "Linear plus sum of odd powers"
    param_names = ("n", "s")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, s: float) -> float:
        """Evaluate ``s*x + (1 - s)*O_n(x) + c``."""
        n_terms = (int(n) - 1) // 2
        x_squared = x * x
        power = x
        sum_of_powers = 0.0
        for _ in range(n_terms):
            power *= x_squared
            sum_of_powers += power
        return s * x + (1.0 - s) * sum_of_powers / n_terms + c

    def interval_bounds(self, n: float, s: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every odd highest power with every slope."""
        return power_and_slope_recipes(LOWEST_POWER)

    def is_param_tuple_valid(self, n: float, s: float) -> bool:
        """Require ``n`` to be an odd integer of at least 5."""
        return is_valid_power(n, LOWEST_POWER)

    test_cases = (
        # O_5(0.5) = (0.125 + 0.03125)/2 = 0.078125
        FormulaTestCase.value(params={"n": 5.0, "s": 0.5}, x=0.5, c=0.0, expected=0.2890625),
        FormulaTestCase.value(params={"n": 5.0, "s": 0.5}, x=0.5, c=0.25, expected=0.5390625),  # exercises c
        FormulaTestCase.value(params={"n": 7.0, "s": 0.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"n": 6.0, "s": 0.5}),  # even highest power
        FormulaTestCase.invalid(params={"n": 5.5, "s": 0.5}),  # highest power that is not an integer
        FormulaTestCase.invalid(params={"n": 3.0, "s": 0.5}),  # a sum of 1 term
        FormulaTestCase.interval_bounds(params={"n": 5.0, "s": 0.5}, expected=(-1.0, 1.0)),
    )
