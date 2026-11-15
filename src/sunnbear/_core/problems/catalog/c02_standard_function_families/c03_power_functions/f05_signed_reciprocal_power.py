"""This formula is a signed reciprocal power, which changes sign through a pole: ``sign(z)*abs(z)^(-p)``."""

import math

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamGrid, ParamRecipe

from .helpers import power_axis

# The function's size never exceeds this value: nearer to the pole, the function is flat at it.
#
# The value is far below float64's largest value on purpose: a solver multiplies function values and their
# differences, and a product of 3 differences of values of this size is still finite.
MAX_ABS_VALUE = 1e100


class SignedReciprocalPower(Formula):
    """`SignedReciprocalPower` is ``sign(z)*abs(z)^(-p)`` with ``z = x - c/(1 + p)``, on ``[-1, 1]``.

    The function has a pole at ``z = 0``, where it jumps from negative to positive values. It has no root: the sign
    change that its interval holds is the pole, which a solver then converges to.

    ``p`` is the power, any value above 0.

    ``c`` shifts x by ``c/(1 + p)``, as in `SignedPower1`, whose class docstring gives the reason for the divisor. The
    pole lies at ``x = c/(1 + p)``.

    The function returns a finite value everywhere:

    - at ``z = 0`` it returns 0;
    - where ``abs(z)^(-p)`` exceeds `MAX_ABS_VALUE`, it returns `MAX_ABS_VALUE` with the sign of ``z``. The function
      is therefore flat within ``MAX_ABS_VALUE^(-1/p)`` of the pole, a distance that grows with ``p``.
    """

    number = (2, 3, 5)
    name = "Signed reciprocal power"
    param_names = ("p",)

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float) -> float:
        """Evaluate ``sign(z)*abs(z)^(-p)`` at ``z = x - c/(1 + p)``, limited to `MAX_ABS_VALUE`, and 0 at ``z = 0``.

        The function computes ``abs(z)^p``, which underflows to 0 next to the pole, and divides by it only where the
        quotient stays within `MAX_ABS_VALUE`. Computing ``abs(z)^(-p)`` directly would overflow there.
        """
        z = x - c / (1.0 + p)
        if z == 0.0:
            return 0.0
        else:
            abs_z_to_p = abs(z) ** p
            if abs_z_to_p * MAX_ABS_VALUE < 1.0:
                return math.copysign(MAX_ABS_VALUE, z)
            else:
                return math.copysign(1.0 / abs_z_to_p, z)

    def interval_bounds(self, p: float) -> tuple[float, float]:
        """Return the interval ``[-1, 1]``, which every parameter tuple shares."""
        return (-1.0, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that sweeps ``p`` from 10^-3 to 10^3.

        At the low end the function is close to the step ``sign(z)``. At the high end it is flat at `MAX_ABS_VALUE` in
        size on most of the interval.
        """
        return (ParamGrid(axes=(power_axis(-3.0, 3.0),)),)

    def is_param_tuple_valid(self, p: float) -> bool:
        """Require ``p`` to be above 0."""
        return p > 0.0

    test_cases = (
        FormulaTestCase.value(params={"p": 1.0}, x=0.5, c=0.0, expected=2.0),
        FormulaTestCase.value(params={"p": 2.0}, x=-0.5, c=0.0, expected=-4.0),  # the sign of z
        FormulaTestCase.value(params={"p": 1.0}, x=0.5, c=0.5, expected=4.0),  # z = 0.5 - 0.5/2
        FormulaTestCase.value(params={"p": 1.0}, x=0.25, c=0.5, expected=0.0),  # at the pole
        FormulaTestCase.value(params={"p": 100.0}, x=0.01, c=0.0, expected=MAX_ABS_VALUE),  # 0.01^-100 is 1e200
        FormulaTestCase.value(params={"p": 100.0}, x=-0.01, c=0.0, expected=-MAX_ABS_VALUE),
        FormulaTestCase.invalid(params={"p": 0.0}),
        FormulaTestCase.invalid(params={"p": -2.0}),
        FormulaTestCase.interval_bounds(params={"p": 2.0}, expected=(-1.0, 1.0)),
    )
