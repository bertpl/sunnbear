"""This formula is a line plus an odd power, ``m*x + (1 - m)*x^p + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_power, power_axis, slope_recipes

# ``LOWEST_POWER`` is the lowest power ``p`` of the formula; every valid power is odd. With ``p = 1`` the function is
# the line ``x + c`` of `Linear` for every ``m``, so ``p = 1`` is not a valid power.
LOWEST_POWER = 3


class LinearPlusOddPower(Formula):
    """`LinearPlusOddPower` is the polynomial ``m*x + (1 - m)*x^p + c`` with an odd power ``p``.

    At ``c = 0`` the function passes through ``(-1, -1)`` and ``(1, 1)``, and is odd-symmetric about its root at 0.

    ``m`` is the slope at ``x = 0``:

    - above ``p/(p - 1)``, the function has a local minimum left of 0 and a local maximum right of 0, beyond which
      it returns to -1 and 1 at the bounds; it keeps 1 root in ``[-1, 1]``;
    - at 1, the function is the line ``x + c``;
    - between 0 and 1, the function is increasing, and it flattens around 0 as ``m`` falls;
    - at 0, the function is the power ``x^p``;
    - below 0, the function has a local maximum left of 0 and a local minimum right of 0, and 3 roots in ``[-1, 1]``
      while ``abs(c)`` stays below the height of those extrema.

    ``c`` adds to the function value, so ``c`` moves the root away from 0. At ``m = 0`` the function is ``x^p + c``,
    whose root has multiplicity ``p`` only at ``c = 0``.
    """

    number = (2, 1, 3)
    name = "Linear plus odd power"
    param_names = ("p", "m")

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float, m: float) -> float:
        """Evaluate ``m*x + (1 - m)*x^p + c``."""
        return m * x + (1.0 - m) * x**p + c

    def interval_bounds(self, p: float, m: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every odd power with every slope."""
        return slope_recipes(power_axis(LOWEST_POWER))

    def is_param_tuple_valid(self, p: float, m: float) -> bool:
        """Require ``p`` to be an odd integer of at least `LOWEST_POWER`."""
        return is_valid_power(p, LOWEST_POWER)

    test_cases = (
        FormulaTestCase.value(params={"p": 3.0, "m": 0.5}, x=0.5, c=0.0, expected=0.3125),  # 0.25 + 0.5*0.125
        FormulaTestCase.value(params={"p": 3.0, "m": 0.5}, x=0.5, c=-0.1, expected=0.2125),  # c shifts the value
        FormulaTestCase.value(params={"p": 3.0, "m": 0.0}, x=0.5, c=0.0, expected=0.125),  # the power alone
        FormulaTestCase.value(params={"p": 5.0, "m": -1.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"p": 4.0, "m": 0.5}),  # even power
        FormulaTestCase.invalid(params={"p": 3.5, "m": 0.5}),  # power that is not an integer
        FormulaTestCase.invalid(params={"p": 1.0, "m": 0.5}),  # power below the lowest one
        FormulaTestCase.interval_bounds(params={"p": 3.0, "m": 0.5}, expected=(-1.0, 1.0)),
    )
