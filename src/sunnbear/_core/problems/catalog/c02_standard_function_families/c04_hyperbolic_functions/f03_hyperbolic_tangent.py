"""This formula is ``1 + tanh(x - c) - d``, which is 0 where ``tanh`` lies ``d`` above its lower asymptote -1."""

import math

from sunnbear._core.problems.core import (
    Formula,
    FormulaParam,
    FormulaTestCase,
    ParamAxis,
    ParamGrid,
    ParamNotation,
    ParamRecipe,
)

# Up to this ``d``, `HyperbolicTangent.parametrized_fun` computes ``1 + tanh(x - c)`` from ``exp(2*(x - c))``
# for ``x < c``, where the root lies in the lower tail of ``tanh``. Above it, ``tanh(x - c) + (1 - d)`` is accurate
# to a few ulps of ``d`` next to the root, because ``abs(1 - d)`` is then below ``d``.
MAX_D_FOR_EXP_EVALUATION = 0.5


class HyperbolicTangent(Formula):
    """`HyperbolicTangent` is ``1 + tanh(x - c) - d`` on ``[-b, b]``.

    - ``b`` is the upper bound of the interval, any value above 0. For a small ``b``, the function is close to a
      line. For a large ``b``, it is close to a step from ``-d`` to ``2 - d``.
    - ``d`` is how far ``tanh`` lies above its lower asymptote -1 at the root, between 0 and 2. At ``d = 1`` the
      function is ``tanh(x - c)``. For a small ``d``, the root lies in ``tanh``'s lower tail, where the function is
      only ``d`` above its value at the lower bound.

    In float64, ``tanh`` equals -1 or 1 outside a range of x about 38 wide, centered on ``x = c``, which is why a large
    ``b`` gives a step.

    A pair of ``b`` and ``d`` is valid only when the root at ``c = 0``, ``x = atanh(d - 1)``, lies inside the interval.

    ``c`` shifts x, so the root lies at ``x = c + atanh(d - 1)``. For a large ``b``, ``c`` moves the step across most
    of the interval.

    References:
        - NIST Digital Library of Mathematical Functions, §4.28, for the definition. https://dlmf.nist.gov/4.28
    """

    number = (2, 4, 3)
    name = "Hyperbolic tangent"
    params = (
        FormulaParam("b"),
        FormulaParam("d"),
    )

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float, d: float) -> float:
        """Evaluate ``1 + tanh(u) - d`` at ``u = x - c``, in the form that keeps full precision next to the root."""
        u = x - c
        if u < 0.0 and d <= MAX_D_FOR_EXP_EVALUATION:
            # 1 + tanh(u) as 2*exp(2*u)/(1 + exp(2*u)): adding 1 to tanh(u) would cancel its leading digits, so next
            # to a root at a small d the function would take only a few values, 1.1e-16 apart.
            exp_2u = math.exp(2.0 * u)
            return 2.0 * exp_2u / (1.0 + exp_2u) - d
        else:
            # At d = 1 this form is tanh(u) itself, which is exactly 0 only at u = 0; the form from exp(2*u) would be
            # 0 on a band about 1e-16 wide.
            return math.tanh(u) + (1.0 - d)

    def interval_bounds(self, b: float, d: float) -> tuple[float, float]:
        """Return the interval ``[-b, b]``."""
        return (-b, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: one that sweeps ``b`` at ``d = 1``, and one that sweeps ``d`` at ``b = 32``.

        - The sweep of ``b``: from 10^-1 to 10^15. From ``b`` of about 10^13 on, the transition of ``tanh`` is narrower
          than the benchmark's ``xtol``, so every solver sees a step.
        - The sweep of ``d``: from 10^-15 to 1. At ``d = 10^-15`` the root lies at about ``x = -17.6``, so the interval
          holds the root at every ``d`` of the sweep.
        """
        return (
            ParamGrid(axes=(ParamAxis("b", -1.0, 15.0, 0.1, ParamNotation.POW10), ParamAxis("d", 1.0, 1.0, 1.0))),
            ParamGrid(axes=(ParamAxis("b", 32.0, 32.0, 1.0), ParamAxis("d", -15.0, 0.0, 0.1, ParamNotation.POW10))),
        )

    def is_param_tuple_valid(self, b: float, d: float) -> bool:
        """Require ``b`` above 0, ``d`` between 0 and 2, and a root inside the interval."""
        if b > 0.0 and 0.0 < d < 2.0:
            return abs(d - 1.0) < math.tanh(b)
        else:
            return False

    test_cases = (
        FormulaTestCase.value(params={"b": 1.0, "d": 1.0}, x=0.5, c=0.5, expected=0.0),  # the root, at x = c
        FormulaTestCase.value(params={"b": 1.0, "d": 1.0}, x=1.0, c=0.0, expected=math.tanh(1.0)),
        FormulaTestCase.value(params={"b": 32.0, "d": 0.5}, x=-math.atanh(0.5), c=0.0, expected=0.0),
        # in the tail: 1 + tanh(-20) is about 2*exp(-40), but adding 1 to tanh(-20) gives 0
        FormulaTestCase.value(
            params={"b": 32.0, "d": 1e-15},
            x=-20.0,
            c=0.0,
            expected=2.0 / (math.exp(40.0) + 1.0) - 1e-15,
            rtol=1e-12,
            atol=0.0,
        ),
        FormulaTestCase.value(params={"b": 32.0, "d": 0.1}, x=1.0, c=0.0, expected=math.tanh(1.0) + 0.9),
        FormulaTestCase.invalid(params={"b": 0.0, "d": 1.0}),
        FormulaTestCase.invalid(params={"b": 1.0, "d": 0.0}),
        FormulaTestCase.invalid(params={"b": 1.0, "d": 2.0}),
        FormulaTestCase.invalid(params={"b": 1.0, "d": 0.1}),  # tanh(1) is about 0.76, so the root lies below -1
        FormulaTestCase.interval_bounds(params={"b": 32.0, "d": 0.5}, expected=(-32.0, 32.0)),
    )
