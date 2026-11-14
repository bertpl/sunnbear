"""This formula is a weighted mean of a line and a power on ``[0, 1]``, ``x/(1 + w) + (w/(1 + w))*x^p - 0.5 + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamGrid, ParamNotation, ParamRecipe

from .helpers import HIGHEST_POWER

# ``LOWEST_POWER`` is the lowest power ``p`` of the formula. With ``p = 1`` the function is the line ``x - 0.5 + c``
# for every ``w``, so ``p = 1`` is not a valid power.
LOWEST_POWER = 2


class OneSidedLinearPlusPower(Formula):
    """`OneSidedLinearPlusPower` is the polynomial ``x/(1 + w) + (w/(1 + w))*x^p - 0.5 + c`` on ``[0, 1]``.

    The interval lies on 1 side of 0, so an even and an odd power ``p`` give the same kind of function: increasing and
    convex, with 1 root. At ``c = 0`` the function passes through ``(0, -0.5)`` and ``(1, 0.5)``, for every ``p`` and
    ``w``, because the weights of the line and the power sum to 1.

    - ``p`` is the power, any integer of at least `LOWEST_POWER`.
    - ``w`` is the weight of the power relative to the line: the power's share is ``w/(1 + w)``. As ``w`` grows, the
      function gets flat near 0 and steep near 1.

    The recipe sweeps ``w`` over a wide range on purpose, wider than the other simple polynomial formulas sweep their
    weights and slopes. At the low end the function is close to a line without being one, and at the high end it is
    close to the power alone, which is very flat for low x.

    ``c`` adds to the function value.
    """

    number = (2, 1, 6)
    name = "One-sided linear plus power"
    param_names = ("p", "w")

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float, w: float) -> float:
        """Evaluate ``x/(1 + w) + (w/(1 + w))*x^p - 0.5 + c``."""
        return (x + w * x**p) / (1.0 + w) - 0.5 + c

    def interval_bounds(self, p: float, w: float) -> tuple[float, float]:
        """Return the interval ``[0, 1]``, which every parameter tuple shares."""
        return (0.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that combines every power with every weight from 10^-6 to 10^6.

        The powers run from `LOWEST_POWER` to `HIGHEST_POWER` in steps of 1, and the weights with the exponent in steps
        of 0.5.
        """
        power_axis = ParamAxis("p", float(LOWEST_POWER), float(HIGHEST_POWER), 1.0)
        weight_axis = ParamAxis("w", -6.0, 6.0, 0.5, ParamNotation.POW10)
        return (ParamGrid(axes=(power_axis, weight_axis)),)

    def is_param_tuple_valid(self, p: float, w: float) -> bool:
        """Require ``p`` to be an integer of at least `LOWEST_POWER`, and ``w`` to be 0 or more."""
        if p != int(p):
            return False
        else:
            return p >= LOWEST_POWER and w >= 0.0

    test_cases = (
        # 0.5/2 + 0.25/2 - 0.5
        FormulaTestCase.value(params={"p": 2.0, "w": 1.0}, x=0.5, c=0.0, expected=-0.125),
        FormulaTestCase.value(params={"p": 2.0, "w": 1.0}, x=0.5, c=0.25, expected=0.125),  # c shifts the value
        FormulaTestCase.value(params={"p": 3.0, "w": 3.0}, x=1.0, c=0.0, expected=0.5),  # through (1, 0.5)
        FormulaTestCase.value(params={"p": 5.0, "w": 0.5}, x=0.0, c=0.0, expected=-0.5),  # through (0, -0.5)
        FormulaTestCase.invalid(params={"p": 2.5, "w": 1.0}),  # power that is not an integer
        FormulaTestCase.invalid(params={"p": 1.0, "w": 1.0}),  # power below the lowest one
        FormulaTestCase.invalid(params={"p": 2.0, "w": -0.5}),  # negative weight
        FormulaTestCase.interval_bounds(params={"p": 2.0, "w": 1.0}, expected=(0.0, 1.0)),
    )
