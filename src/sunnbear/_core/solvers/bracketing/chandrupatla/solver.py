"""`Chandrupatla` implements Chandrupatla's method: inverse quadratic interpolation where well conditioned."""

import math

from sunnbear._core.solvers.core import Solver, SolveState


class Chandrupatla(Solver):
    """`Chandrupatla` implements Chandrupatla's method, as the BASIC listing ``NEWZERO.BAS`` of its paper.

    The paper is Chandrupatla, Advances in Engineering Software 28, 1997.

    The method keeps 3 points: ``x1``, the newest point; ``x2``, the other interval bound, where ``f`` has the other
    sign; and ``x3``, the point discarded last. Each iteration evaluates ``x = x1 + t * (x2 - x1)``, with ``t`` from 1
    of 2 steps:

    - inverse quadratic interpolation through the 3 points, where the paper shows it to be well conditioned:
      ``1 - sqrt(1 - xi) < phi < sqrt(xi)``, with ``xi = (x1 - x2) / (x3 - x2)`` and
      ``phi = (f1 - f2) / (f3 - f2)``;
    - bisection, ``t = 0.5``, everywhere else, and in the first iteration.

    ``t`` is then kept at least ``tl = tol / |x2 - x1|`` away from 0 and 1, so that every new point lies at least
    ``tol`` inside the interval.

    The paper's tolerance is ``tol = 2 * eps_r * |xm| + 0.5 * eps_a``, with a relative tolerance ``eps_r``, an
    absolute tolerance ``eps_a``, and ``xm`` the interval bound with the smaller ``|f|``. The solver passes ``xtol``
    as ``eps_a`` and 0 as ``eps_r``, so ``tol = 0.5 * xtol``. The solve ends once ``tl > 0.5``, that is once the
    interval is narrower than ``xtol``, or once ``f(xm)`` is 0. It returns ``xm``, which then lies within ``xtol`` of
    the root.

    The 3 points change roles as the iteration proceeds, and the stopping criterion is the paper's own, so
    `Chandrupatla` writes its own loop, not `BracketingSolver`'s.
    """

    name = "chandrupatla"
    version = 1

    def _solve(self, state: SolveState) -> float:
        """Run the loop of the paper's BASIC listing and return ``xm``.

        The variables keep the names of the BASIC listing, so that the code can be compared with the listing line by
        line. Besides the ones that the class docstring defines, ``fi`` is ``f(xi)``, ``ph`` is ``phi``, ``fl`` and
        ``fh`` are the lower and upper limits on ``phi``, ``al`` is ``(x3 - x1) / (x2 - x1)``, and ``a``, ``b``,
        ``c`` and ``d`` are the 4 quotients that make up the interpolated ``t``.

        Each iteration:

        - evaluates ``x`` and makes it ``x1``;
        - ends the solve if the stopping criterion holds;
        - chooses ``t`` for the next iteration.
        """
        interval = state.interval
        x1, f1, x2, f2 = interval.a, interval.fa, interval.b, interval.fb
        tol = 0.5 * state.xtol
        t = 0.5
        while True:
            # --- the new point x ----------------
            x = x1 + t * (x2 - x1)
            f = state.f(x)
            state.x_best = x
            # Arrange 2-1-3: 2-1 is the interval, 1 its newest point, 3 the point discarded last. An exact zero f may
            # take either branch, since the stopping criterion below then returns x.
            if (f > 0.0) == (f1 > 0.0):
                x3, f3 = x1, f1
            else:
                x3, f3 = x2, f2
                x2, f2 = x1, f1
            x1, f1 = x, f

            # --- the stopping criterion ---------
            # xm is the interval bound with the smaller |f|, and the newest point when both are equal.
            xm, fm = x1, f1
            if abs(f2) < abs(f1):
                xm, fm = x2, f2
            tl = tol / abs(x2 - x1)
            if tl > 0.5 or fm == 0.0:
                return xm

            # --- t for the next point -----------
            xi = (x1 - x2) / (x3 - x2)
            ph = (f1 - f2) / (f3 - f2)
            fl = 1.0 - math.sqrt(1.0 - xi)
            fh = math.sqrt(xi)
            if fl < ph and ph < fh:
                # The inverse quadratic interpolation is well conditioned, so it gives t.
                al = (x3 - x1) / (x2 - x1)
                a = f1 / (f2 - f1)
                b = f3 / (f2 - f3)
                c = f1 / (f3 - f1)
                d = f2 / (f3 - f2)
                t = a * b + c * d * al
            else:
                t = 0.5
            # Keep t at least tl away from 0 and 1.
            if t < tl:
                t = tl
            if t > 1.0 - tl:
                t = 1.0 - tl
