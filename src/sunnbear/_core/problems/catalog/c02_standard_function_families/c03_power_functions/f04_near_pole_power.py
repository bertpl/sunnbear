"""This formula is a reciprocal power on an interval that starts near its pole, ``(d/x)^p - 0.5 + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamGrid, ParamRecipe

from .helpers import distance_axis, power_axis


class NearPolePower(Formula):
    """`NearPolePower` is the reciprocal power ``(d/x)^p - 0.5 + c`` on ``[d, 1]``.

    The reciprocal power ``x^(-p)`` has a pole at ``x = 0``. The function is decreasing and convex, and steepest at the
    lower bound.

    - ``p`` is the power, any value above 0.
    - ``d`` is the distance from the pole to the lower bound of the interval, above 0.

    The formula divides ``x^(-p)`` by its value at the lower bound, ``d^(-p)``, which gives ``(d/x)^p``. The power is
    then 1 at the lower bound for every ``p`` and ``d``, and the formula never computes ``d^(-p)``, which overflows
    float64 for a large ``p``.

    At ``c = 0`` the function is 0.5 at the lower bound and ``d^p - 0.5`` at the upper bound. A pair of ``p`` and
    ``d`` is valid only when ``d^p < 0.5``, so that the function has a root inside the interval.

    ``c`` adds to the function value, so the root lies at ``d*(0.5 - c)^(-1/p)``, the lower bound times a factor that
    nears 1 as ``p`` grows.
    """

    number = (2, 3, 4)
    name = "Near-pole power"
    param_names = ("p", "d")

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float, d: float) -> float:
        """Evaluate ``(d/x)^p - 0.5 + c``."""
        return (d / x) ** p - 0.5 + c

    def interval_bounds(self, p: float, d: float) -> tuple[float, float]:
        """Return the interval ``[d, 1]``."""
        return (d, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipe that combines ``p`` from 10^-2 to 10^6 with every distance of `distance_axis`.

        The recipe does not leave out the candidates that fail the benchmark suite inclusion conditions. For a large
        ``p`` at a small ``d``, the root lies too close to the lower bound to satisfy them, so no benchmark suite holds
        such a candidate.
        """
        return (ParamGrid(axes=(power_axis(-2.0, 6.0), distance_axis())),)

    def is_param_tuple_valid(self, p: float, d: float) -> bool:
        """Require ``p`` and ``d`` above 0, and a root inside the interval."""
        if p > 0.0 and d > 0.0:
            return d**p < 0.5
        else:
            return False

    test_cases = (
        FormulaTestCase.value(params={"p": 1.0, "d": 0.1}, x=0.2, c=0.0, expected=0.0),  # the root, at d*2^(1/p)
        FormulaTestCase.value(params={"p": 2.0, "d": 0.1}, x=0.1, c=0.0, expected=0.5),  # at the lower bound
        FormulaTestCase.value(params={"p": 2.0, "d": 0.1}, x=1.0, c=0.2, expected=-0.29),  # 0.01 - 0.5 + 0.2
        FormulaTestCase.invalid(params={"p": 0.1, "d": 0.1}),  # 0.1^0.1 is about 0.79, so no root in the interval
        FormulaTestCase.invalid(params={"p": 1.0, "d": 0.0}),  # the pole at the lower bound
        FormulaTestCase.invalid(params={"p": 0.0, "d": 0.1}),
        FormulaTestCase.interval_bounds(params={"p": 1.0, "d": 0.1}, expected=(0.1, 1.0)),
    )
