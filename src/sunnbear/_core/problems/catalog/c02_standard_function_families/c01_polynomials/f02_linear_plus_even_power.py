"""This formula is a line plus an even power, ``x + p*(x^n - 1) + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamRecipe

from .helpers import is_valid_n, power_and_weight_recipes

# ``LOWEST_N`` is the lowest power ``n`` of the formula; every valid power is even.
LOWEST_N = 2


class LinearPlusEvenPower(Formula):
    """`LinearPlusEvenPower` is the polynomial ``x + p*(x^n - 1) + c`` with an even power ``n``.

    At ``c = 0`` the function passes through ``(-1, -1)`` and ``(1, 1)``. For a positive weight ``p`` the function is
    convex, and at ``c = 0`` it has 1 root in ``[-1, 1]``, to the right of 0.

    - ``p`` is the weight of the power term. As ``p`` grows, the root moves toward the right bound and the curvature
      at the root grows.
    - ``n`` sets where the function bends: a higher power leaves the function nearly linear around 0 and bends it
      closer to the bounds.

    ``c`` adds to the function value, so the values at the bounds are ``-1 + c`` and ``1 + c`` for every ``n`` and
    ``p``.
    """

    number = (2, 1, 2)
    name = "Linear plus even power"
    param_names = ("n", "p")

    @staticmethod
    def parametrized_fun(x: float, c: float, n: float, p: float) -> float:
        """Evaluate ``x + p*(x^n - 1) + c``."""
        return x + p * (x**n - 1.0) + c

    def interval_bounds(self, n: float, p: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes that combine every even power with every weight."""
        return power_and_weight_recipes(LOWEST_N)

    def is_param_tuple_valid(self, n: float, p: float) -> bool:
        """Require ``n`` to be an even integer of at least `LOWEST_N`."""
        return is_valid_n(n, LOWEST_N)

    test_cases = (
        FormulaTestCase.value(params={"n": 2.0, "p": 0.5}, x=0.5, c=0.0, expected=0.125),  # 0.5 + 0.5*(0.25 - 1)
        FormulaTestCase.value(params={"n": 2.0, "p": 0.5}, x=0.5, c=0.25, expected=0.375),  # c shifts the value
        FormulaTestCase.value(params={"n": 4.0, "p": 2.0}, x=-1.0, c=0.0, expected=-1.0),  # through (-1, -1)
        FormulaTestCase.invalid(params={"n": 3.0, "p": 0.5}),  # odd power
        FormulaTestCase.invalid(params={"n": 2.5, "p": 0.5}),  # power that is not an integer
        FormulaTestCase.invalid(params={"n": 0.0, "p": 0.5}),  # power below the lowest one
        FormulaTestCase.interval_bounds(params={"n": 2.0, "p": 0.5}, expected=(-1.0, 1.0)),
    )
