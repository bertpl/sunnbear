"""This formula is ``(2/pi)*atan(x - c) + 1 - d``, which is 0 where ``(2/pi)*atan`` lies ``d`` above -1."""

import math

from sunnbear._core.problems.core import (
    EffectOfC,
    Formula,
    FormulaParam,
    FormulaPresentation,
    FormulaTestCase,
    ParamAxis,
    ParamGrid,
    ParamNotation,
    ParamRecipe,
)

# Up to this ``d``, `InverseTangent.parametrized_fun` computes ``(2/pi)*atan(u) + 1`` from ``atan(-1/u)`` for ``u < 0``,
# where the root lies in the lower tail of ``atan``. Above it, ``(2/pi)*atan(u) + (1 - d)`` is accurate to a few ulps of
# ``d`` next to the root, because ``abs(1 - d)`` is then below ``d``.
MAX_D_FOR_TAIL_EVALUATION = 0.5


class InverseTangent(Formula):
    """`InverseTangent` is ``(2/pi)*atan(x - c) + 1 - d`` on ``[-b, b]``.

    ``(2/pi)*atan`` is a step from -1 to 1 whose tails approach their asymptotes only as ``1/x``:
    ``(2/pi)*atan(x)`` is about ``1 - 2/(pi*x)`` for a large ``x``. The function's plateaus lie at ``-d`` and
    ``2 - d``.

    - ``b`` is the upper bound of the interval, any value above 0, and sets the slope of the step relative to the
      interval. For a small ``b``, the function is close to a line. For a large ``b``, it is close to a step.
    - ``d`` is how far ``(2/pi)*atan`` lies above its lower asymptote -1 at the root, between 0 and 2. At ``d = 1`` the
      function is ``(2/pi)*atan(x - c)``. For a small ``d``, the root lies far out in the lower tail, at about
      ``x = c - 2/(pi*d)``, where the function is close to its lower plateau.

    A pair of ``b`` and ``d`` is valid only when the root at ``c = 0``, ``x = tan(pi/2*(d - 1))``, lies inside the
    interval.

    ``c`` shifts x, so the step lies at ``x = c``, and the root keeps its distance from the step.

    References:
        - NIST Digital Library of Mathematical Functions, §4.23, for the definition. https://dlmf.nist.gov/4.23
    """

    number = (2, 6, 6)
    name = "Inverse tangent"
    params = (
        FormulaParam("b", latex_symbol="b"),
        FormulaParam(
            "d",
            latex_symbol="d",
            meaning=r"The height of $\frac{2}{\pi} \arctan$ above its lower asymptote, $-1$, at the root.",
        ),
    )
    presentation = FormulaPresentation(
        definitions=((r"\tmp{u}", r"\x - \c"),),
        expression=(
            r"\begin{cases} "
            r"\frac{2}{\pi} \arctan\left(-\frac{1}{\tmp{u}}\right) - \param{d} "
            r"& \text{if } \tmp{u} < 0 \text{ and } \param{d} \le 0.5 \\ "
            r"\frac{2}{\pi} \arctan(\tmp{u}) + (1 - \param{d}) & \text{otherwise} "
            r"\end{cases}"
        ),
        interval=r"[-\param{b}, \param{b}]",
        summary=(
            "The inverse tangent, a step whose tails approach their plateaus only as the reciprocal of the distance "
            "from the step, with the root in the step or far out in the step's lower tail."
        ),
        notes=(
            r"Both cases equal $$\frac{2}{\pi} \arctan(\x - \c) + 1 - \param{d};$$ the first keeps full precision next "
            r"to a root in the lower tail of $\arctan$.",
        ),
        param_conditions=(
            r"$\param{b} > 0$",
            r"$0 < \param{d} < 2$",
            r"$|\param{d} - 1| < \frac{2}{\pi} \arctan(\param{b})$, so that the root lies inside the interval",
        ),
    )
    effect_of_c = EffectOfC.SHIFTS_X

    @staticmethod
    def parametrized_fun(x: float, c: float, b: float, d: float) -> float:
        """Evaluate ``(2/pi)*atan(u) + 1 - d`` at ``u = x - c``, in the form that keeps full precision at the root."""
        u = x - c
        if u < 0.0 and d <= MAX_D_FOR_TAIL_EVALUATION:
            # (2/pi)*atan(u) + 1 as (2/pi)*atan(-1/u): adding 1 to (2/pi)*atan(u) would cancel its leading digits, so
            # next to a root at a small d the function would take only a few values, 1.1e-16 apart.
            return (2.0 / math.pi) * math.atan(-1.0 / u) - d
        else:
            # At d = 1 this form is (2/pi)*atan(u) itself, which is exactly 0 only at u = 0; the form from atan(-1/u)
            # would be 0 on a band about 1e-16 wide.
            return (2.0 / math.pi) * math.atan(u) + (1.0 - d)

    def interval_bounds(self, b: float, d: float) -> tuple[float, float]:
        """Return the interval ``[-b, b]``."""
        return (-b, b)

    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return 2 recipes: one that sweeps ``b`` at ``d = 1``, and one that sweeps ``d`` at ``b = 2^30``.

        - The sweep of ``b``: from 2^-10 to 2^50, about 1.1e15. At the high end, ``atan`` differs from its asymptotes by
          less than 10 ulps wherever x lies farther than ``b/2`` from the step, so solvers see close to a step.
        - The sweep of ``d``: from 2^-30 to 1. At ``d = 2^-30`` the root at ``c = 0`` lies at about ``-0.64*b``, where f
          is only about ``d`` above its value at the lower bound. The benchmark's ``xtol`` at this ``b`` is about 1e-3,
          so the root lies many ``xtol`` away from the step at every ``d`` of the sweep but 1.
        """
        return (
            ParamGrid(
                axes=(ParamAxis("b", -10.0, 50.0, 0.1, ParamNotation.POW2), ParamAxis("d", 1.0, 1.0, 1.0)),
                summary=r"The sweep of $\param{b}$ from $2^{-10}$ to $2^{50}$ at $\param{d} = 1$.",
            ),
            ParamGrid(
                axes=(
                    ParamAxis("b", 30.0, 30.0, 1.0, ParamNotation.POW2),
                    ParamAxis("d", -30.0, 0.0, 0.1, ParamNotation.POW2),
                ),
                summary=r"The sweep of $\param{d}$ from $2^{-30}$ to 1 at $\param{b} = 2^{30}$.",
            ),
        )

    def is_param_tuple_valid(self, b: float, d: float) -> bool:
        """Check the parameter conditions listed in the presentation's `param_conditions`."""
        if b > 0.0 and 0.0 < d < 2.0:
            return abs(d - 1.0) < (2.0 / math.pi) * math.atan(b)
        else:
            return False

    test_cases = (
        FormulaTestCase.value(params={"b": 1.0, "d": 1.0}, x=0.5, c=0.5, expected=0.0),  # the root, at x = c
        FormulaTestCase.value(params={"b": 1.0, "d": 1.0}, x=1.0, c=0.0, expected=0.5),  # (2/pi)*atan(1)
        FormulaTestCase.value(params={"b": 32.0, "d": 0.5}, x=-1.0, c=0.0, expected=0.0),  # (2/pi)*atan(-1) = -0.5
        # in the tail: (2/pi)*atan(-1e9) + 1 is about 2/(pi*1e9), but adding 1 to (2/pi)*atan(-1e9) loses 7 digits
        FormulaTestCase.value(
            params={"b": 2.0**30, "d": 1e-9},
            x=-1e9,
            c=0.0,
            expected=(2.0 / math.pi) * math.atan(1e-9) - 1e-9,
            rtol=1e-12,
            atol=0.0,
        ),
        FormulaTestCase.value(
            params={"b": 32.0, "d": 0.75}, x=2.0, c=0.0, expected=(2.0 / math.pi) * math.atan(2.0) + 0.25
        ),
        FormulaTestCase.invalid(params={"b": 0.0, "d": 1.0}),
        FormulaTestCase.invalid(params={"b": 1.0, "d": 0.0}),
        FormulaTestCase.invalid(params={"b": 1.0, "d": 2.0}),
        FormulaTestCase.invalid(params={"b": 1.0, "d": 0.1}),  # (2/pi)*atan(1) is 0.5, so the root lies below -1
        FormulaTestCase.interval_bounds(params={"b": 32.0, "d": 0.5}, expected=(-32.0, 32.0)),
    )
