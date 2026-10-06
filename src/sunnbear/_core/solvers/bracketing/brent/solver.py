"""`Brent` implements Brent's method: interpolation steps that bisection takes over when they converge too slowly."""

import sys

from sunnbear._core.solvers.core import Solver, SolveState

# Brent's ``macheps``, the relative machine precision: 2^-52 for float64.
_MACHEPS = sys.float_info.epsilon


class Brent(Solver):
    """`Brent` implements Brent's method, as the Algol 60 procedure ``zero`` (Brent, The Computer Journal 14, 1971).

    Each iteration evaluates 1 point, reached by 1 of 3 steps from the best point so far:

    - inverse quadratic interpolation through the last 3 points;
    - linear interpolation, a secant step, when only 2 distinct points are known;
    - bisection, forced when the step before the previous one was shorter than the tolerance, or when the last step
      did not reduce ``|f|``; it also replaces an interpolation step that lands too close to the far bound or is
      not shorter than half the step before the previous one.

    A step shorter than the tolerance is lengthened to the tolerance, toward the other bound. These rules guarantee
    that the solve converges within a bounded number of evaluations, whatever the function.

    The variables keep the names of the Algol procedure, so that the code can be compared with it line by line:

    - ``b`` and ``c`` are the interval bounds, ``b`` the one with the smaller ``|f|``, which is the best estimate;
    - ``a`` is the previous value of ``b``;
    - ``d`` is the step from ``b`` in this iteration, and ``e`` the step of the iteration before;
    - ``m`` is half the signed width of the interval, from ``b`` toward ``c``;
    - ``p / q`` is the interpolation step, computed as a separate numerator and denominator so that the step is
      only divided out once it is accepted;
    - ``tol = 2 * macheps * |b| + t``, the tolerance; the solve ends once ``|m| <= tol`` or ``f(b) = 0``, and
      returns ``b``.

    Brent's procedure returns a ``b`` within ``6 * macheps * |x| + 2 * t`` of a root ``x``, where ``macheps`` is
    the relative machine precision, and ``t`` is its absolute tolerance. The solver sets
    ``t = (xtol - 6 * macheps * max(|a|, |b|)) / 2``, with ``a`` and ``b`` the bounds of the initial interval, so
    that the returned ``b`` lies within ``xtol`` of a root. ``xtol`` must therefore exceed
    ``6 * macheps * max(|a|, |b|)``; below that, the tolerance can never be met, and the solve runs until its
    evaluation budget is exhausted.

    The bounds ``b`` and ``c`` swap roles as the iteration proceeds, and the stopping criterion is Brent's own, so
    `Brent` writes its own loop, not `BracketingSolver`'s.
    """

    name = "brent"
    version = 1

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — 1 loop that follows Brent's procedure line by line
        """Run Brent's procedure and return ``b``.

        Each iteration makes ``b`` the bound with the smaller ``|f|``, and ends the solve if the stopping criterion
        holds. Otherwise it chooses the step ``d``, evaluates ``b + d``, and keeps the bound on the other side of
        the root as ``c``.
        """
        interval = state.interval
        a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb
        t = 0.5 * (state.xtol - 6.0 * _MACHEPS * max(abs(a), abs(b)))
        # The Algol label "int": the previous value of b, which lies on the other side of the root, becomes c.
        c, fc = a, fa
        d = e = b - a
        while True:
            # --- the Algol label "ext" -------
            if abs(fc) < abs(fb):
                a, b, c = b, c, b
                fa, fb, fc = fb, fc, fb
            tol = 2.0 * _MACHEPS * abs(b) + t
            m = 0.5 * (c - b)
            if abs(m) <= tol or fb == 0.0:
                return b

            # --- the step d ------------------
            if abs(e) < tol or abs(fa) <= abs(fb):
                d = e = m  # A bisection is forced.
            else:
                s = fb / fa
                if a == c:
                    # Linear interpolation, through b and c.
                    p = 2.0 * m * s
                    q = 1.0 - s
                else:
                    # Inverse quadratic interpolation, through a, b and c.
                    q = fa / fc
                    r = fb / fc
                    p = s * (2.0 * m * q * (q - r) - (b - a) * (r - 1.0))
                    q = (q - 1.0) * (r - 1.0) * (s - 1.0)
                if p > 0.0:
                    q = -q
                else:
                    p = -p
                s = e
                e = d
                if 2.0 * p < 3.0 * m * q - abs(tol * q) and p < abs(0.5 * s * q):
                    d = p / q
                else:
                    d = e = m

            # --- the evaluation at b + d -----
            a, fa = b, fb
            if abs(d) > tol:
                b = b + d
            elif m > 0.0:
                b = b + tol
            else:
                b = b - tol
            fb = state.f(b)
            state.x_best = b
            if (fb > 0.0) == (fc > 0.0):
                # The Algol label "int": b crossed the root, so its previous value a becomes c.
                c, fc = a, fa
                d = e = b - a
