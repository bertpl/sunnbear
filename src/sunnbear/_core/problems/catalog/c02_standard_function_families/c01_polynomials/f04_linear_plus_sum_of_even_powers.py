"""This formula is a line plus the mean of the even powers up to ``n``, ``x + p*(E_n(x) - 1) + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_power, power_and_weight_recipes

# The lowest highest-power ``n`` of the formula, which gives a sum of 2 terms; every valid ``n`` is even. With
# ``n = 2`` the function is `LinearPlusEvenPower`'s.
LOWEST_POWER = 4


class LinearPlusSumOfEvenPowers(Formula):
    """`LinearPlusSumOfEvenPowers` is the polynomial ``x + p*(E_n(x) - 1) + c`` with an even highest power ``n``.

    ``E_n(x) = (x^2 + x^4 + ... + x^n)/k`` is the mean of the ``k = n/2`` even powers up to ``n``. Dividing by ``k``
    makes the function pass through ``(-1, -1)`` and ``(1, 1)`` at ``c = 0``, for every ``n`` and ``p``.

    - ``p`` is the weight of the sum, as in `LinearPlusEvenPower`.
    - ``n`` adds higher powers, which steepen the function toward the bounds. The term ``x^2`` keeps the function
      curved around 0 for every ``n``, where a single high power is nearly flat.

    ``c`` adds to the function value.
    """

    number = (2, 1, 4)
    name = "Linear plus sum of even powers"
    param_names = ("n", "p")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, p: float) -> float:
        """Evaluate ``x + p*(E_n(x) - 1) + c``."""
        n_terms = int(n) // 2
        x_squared = x * x
        power = 1.0
        sum_of_powers = 0.0
        for _ in range(n_terms):
            power *= x_squared
            sum_of_powers += power
        return x + p * (sum_of_powers / n_terms - 1.0) + c

    def interval_bounds(self, n: float, p: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every even highest power with every weight."""
        return power_and_weight_recipes(LOWEST_POWER)

    def is_param_tuple_valid(self, n: float, p: float) -> bool:
        """Require ``n`` to be an even integer of at least 4."""
        return is_valid_power(n, LOWEST_POWER)

    test_cases = (
        # E_4(0.5) = (0.25 + 0.0625)/2 = 0.15625
        FormulaTestCase.value(params={"n": 4.0, "p": 1.0}, x=0.5, c=0.0, expected=-0.34375),
        FormulaTestCase.value(params={"n": 4.0, "p": 1.0}, x=0.5, c=0.5, expected=0.15625),  # exercises c
        FormulaTestCase.value(params={"n": 6.0, "p": 2.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"n": 5.0, "p": 1.0}),  # odd highest power
        FormulaTestCase.invalid(params={"n": 4.5, "p": 1.0}),  # highest power that is not an integer
        FormulaTestCase.invalid(params={"n": 2.0, "p": 1.0}),  # a sum of 1 term
        FormulaTestCase.interval_bounds(params={"n": 4.0, "p": 1.0}, expected=(-1.0, 1.0)),
    )
