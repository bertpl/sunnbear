"""This formula is a power on an interval that starts at or near the edge of its domain, ``x^p - 0.5 + c``."""

from sunnbear._core.problems.core import Formula, FormulaTestCase, ParamAxis, ParamGrid, ParamRecipe

from .helpers import distance_axis, power_axis

# Both recipes start their sweep of ``p`` at ``10^LOWEST_LOG10_POWER``.
LOWEST_LOG10_POWER = -2.0


class NearEdgePower(Formula):
    """`NearEdgePower` is the power ``x^p - 0.5 + c`` on ``[d, 1]``.

    The edge is the edge of the power's domain, ``x = 0``: for a ``p`` that is not an integer, ``x^p`` has no real
    value at a negative x.

    - ``p`` is the power, any value above 0. Below ``p = 1`` the function is a root function such as the square root,
      whose slope grows without limit toward the edge. Above ``p = 1`` the function is flat at the edge.
    - ``d`` is the distance from the edge to the lower bound of the interval, 0 or more. At ``d = 0`` the interval
      starts at the edge.

    At ``c = 0`` the function is 0.5 at the upper bound and ``d^p - 0.5`` at the lower bound. A pair of ``p`` and
    ``d`` is valid only when ``d^p < 0.5``, so that the function has a root inside the interval.

    ``c`` adds to the function value, so the root lies at ``(0.5 - c)^(1/p)``. For a small ``p`` the root lies next
    to the edge, and for a large ``p`` next to the upper bound.
    """

    number = (2, 3, 3)
    name = "Near-edge power"
    param_names = ("p", "d")

    @staticmethod
    def parametrized_fun(x: float, c: float, p: float, d: float) -> float:
        """Evaluate ``x^p - 0.5 + c``."""
        return x**p - 0.5 + c

    def interval_bounds(self, p: float, d: float) -> tuple[float, float]:
        """Return the interval ``[d, 1]``."""
        return (d, 1.0)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: one for the interval that starts at the edge, and one for the intervals that start near it.

        - At the edge: ``d = 0``, with ``p`` up to 10^6.
        - Near the edge: every distance of `distance_axis`, with ``p`` up to 1. Above ``p = 1`` the function is flat
          near the edge, so a small ``d`` barely changes it.

        Both recipes start ``p`` at the same round value, ``10^LOWEST_LOG10_POWER``, and neither leaves out the
        candidates that fail the benchmark suite inclusion conditions. For a small ``p`` at ``d = 0``, the root lies
        too close to the lower bound to satisfy them, so no benchmark suite holds such a candidate.
        """
        zero_distance_axis = ParamAxis("d", 0.0, 0.0, 1.0)
        return (
            ParamGrid(axes=(power_axis(LOWEST_LOG10_POWER, 6.0), zero_distance_axis)),
            ParamGrid(axes=(power_axis(LOWEST_LOG10_POWER, 0.0), distance_axis())),
        )

    def is_param_tuple_valid(self, p: float, d: float) -> bool:
        """Require ``p`` above 0, ``d`` of 0 or more, and a root inside the interval."""
        if p > 0.0 and d >= 0.0:
            return d**p < 0.5
        else:
            return False

    test_cases = (
        FormulaTestCase.value(params={"p": 0.5, "d": 0.0}, x=0.25, c=0.0, expected=0.0),  # the root, at 0.5^(1/p)
        FormulaTestCase.value(params={"p": 2.0, "d": 0.0}, x=0.5, c=0.1, expected=-0.15),  # c shifts the value
        FormulaTestCase.value(params={"p": 0.5, "d": 0.0}, x=0.0, c=0.0, expected=-0.5),  # at the edge
        FormulaTestCase.value(params={"p": 1.0, "d": 0.1}, x=1.0, c=0.0, expected=0.5),  # at the upper bound
        FormulaTestCase.invalid(params={"p": 0.1, "d": 0.1}),  # 0.1^0.1 is about 0.79, so no root in the interval
        FormulaTestCase.invalid(params={"p": 0.0, "d": 0.0}),
        FormulaTestCase.invalid(params={"p": 1.0, "d": -0.1}),
        FormulaTestCase.interval_bounds(params={"p": 2.0, "d": 0.0}, expected=(0.0, 1.0)),
        FormulaTestCase.interval_bounds(params={"p": 1.0, "d": 0.1}, expected=(0.1, 1.0)),
    )
