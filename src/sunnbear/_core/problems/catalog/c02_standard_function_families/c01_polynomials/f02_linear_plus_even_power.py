"""This formula is a line plus an even power, ``x + w*(x^p - 1) + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_power, power_axis, weight_recipes

# ``LOWEST_POWER`` is the lowest power ``p`` of the formula; every valid power is even.
LOWEST_POWER = 2


class LinearPlusEvenPower(Formula):
    """`LinearPlusEvenPower` is the polynomial ``x + w*(x^p - 1) + c`` with an even power ``p``.

    At ``c = 0`` the function passes through ``(-1, -1)`` and ``(1, 1)``. For a positive weight ``w`` the function is
    convex, and at ``c = 0`` it has 1 root in ``[-1, 1]``, to the right of 0.

    - ``w`` is the weight of the power term. As ``w`` grows, the root moves toward the right bound and the curvature
      at the root grows.
    - ``p`` sets where the function bends: a higher power leaves the function nearly linear around 0 and bends it
      closer to the bounds.

    ``c`` adds to the function value, so the values at the bounds are ``-1 + c`` and ``1 + c`` for every ``p`` and
    ``w``.
    """

    number = (2, 1, 2)
    name = "Linear plus even power"
    param_names = ("p", "w")

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float, w: float) -> float:
        """Evaluate ``x + w*(x^p - 1) + c``."""
        return x + w * (x**p - 1.0) + c

    def interval_bounds(self, p: float, w: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every even power with every weight."""
        return weight_recipes(power_axis(LOWEST_POWER))

    def is_param_tuple_valid(self, p: float, w: float) -> bool:
        """Require ``p`` to be an even integer of at least `LOWEST_POWER`."""
        return is_valid_power(p, LOWEST_POWER)

    test_cases = (
        FormulaTestCase.value(params={"p": 2.0, "w": 0.5}, x=0.5, c=0.0, expected=0.125),  # 0.5 + 0.5*(0.25 - 1)
        FormulaTestCase.value(params={"p": 2.0, "w": 0.5}, x=0.5, c=0.25, expected=0.375),  # c shifts the value
        FormulaTestCase.value(params={"p": 4.0, "w": 2.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"p": 3.0, "w": 0.5}),  # odd power
        FormulaTestCase.invalid(params={"p": 2.5, "w": 0.5}),  # power that is not an integer
        FormulaTestCase.invalid(params={"p": 0.0, "w": 0.5}),  # power below the lowest one
        FormulaTestCase.interval_bounds(params={"p": 2.0, "w": 0.5}, expected=(-1.0, 1.0)),
    )
