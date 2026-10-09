"""`Brent` implements Brent's method: interpolation steps, with bisection when they converge too slowly."""

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.utils.floats import FLOAT64_EPS


class Brent(Solver):
    """`Brent` implements Brent's method, as the Algol 60 procedure ``zero`` (Brent, 1971).

    Each iteration evaluates 1 point, reached by 1 of 3 steps from the best point so far:

    - inverse quadratic interpolation through the last 3 points;
    - linear interpolation, a secant step, when only 2 distinct points are known;
    - bisection, in 2 cases:

      - forced, when the step before the previous one was shorter than the tolerance ``tol`` (defined below), or
        when the last step did not reduce ``|f|``;
      - in place of an interpolation step that lands more than 3/4 of the way from the best point to the other
        bound, or that is not shorter than half the step before the previous one.

    A step shorter than the tolerance is lengthened to the tolerance, toward the bound on the other side of the root.
    As long as ``tol`` stays positive, these rules guarantee that the solve converges within a bounded number of
    evaluations, at most about the square of bisection's count, whatever the function.

    The stopping criterion and the tolerance use these quantities of Brent's procedure:

    - ``b`` and ``c`` are the interval bounds, ``b`` the one with the smaller ``|f|``, which is the best estimate;
    - ``m`` is half the signed width of the interval, from ``b`` toward ``c``;
    - ``tol = 2 * macheps * |b| + t`` is the tolerance, with ``macheps`` the relative machine precision
      (`FLOAT64_EPS`) and ``t`` an absolute tolerance derived from ``xtol`` (below); the solve ends once
      ``|m| <= tol`` or ``f(b) = 0``, and returns ``b``.

    Brent's procedure returns a ``b`` within ``6 * macheps * |x| + 2 * t`` of a root ``x``. The solver sets
    ``t = (xtol - 6 * macheps * max(|a0|, |b0|)) / 2``, with ``a0`` and ``b0`` the bounds of the initial interval,
    so that the returned ``b`` lies within ``xtol`` of a root.

    ``xtol`` must therefore exceed ``6 * macheps * max(|a0|, |b0|)``; below that, ``t`` is negative and the accuracy
    is no longer guaranteed. Where ``t`` is so negative that ``tol`` is negative too, ``|m| <= tol`` can never hold, and
    the solve runs until its evaluation budget is exhausted.

    The bounds ``b`` and ``c`` swap roles as the iteration proceeds, and the stopping criterion is Brent's own, so
    `Brent` writes its own loop, not `BracketingSolver`'s.

    References:
        - Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. The
          Computer Journal 14(4), 422-425. The paper's appendix holds the Algol 60 procedure ``zero``.
          https://doi.org/10.1093/comjnl/14.4.422
        - SciPy's ``scipy.optimize.brentq``; the test suite checks `Brent` against ``scipy.optimize.brentq``.
    """

    name = "brent"
    version = 1

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the line-by-line match with Brent's procedure
        """Run Brent's procedure and return ``b``.

        The variables keep the names of the Algol procedure, and comments mark where its labels ``int`` and ``ext``
        fall, so that the code can be compared with the procedure line by line. Besides ``b``, ``c``, ``m`` and
        ``tol``, which the class docstring defines:

        - ``a`` is the previous value of ``b``;
        - ``d`` is the step taken from ``b``, and ``e`` the step taken in the iteration before it; while the next
          step is chosen, ``d`` therefore holds the previous step and ``e`` the step before the previous one;
        - ``p / q`` is the interpolation step, computed as a separate numerator and denominator so that the division
          ``p / q`` runs only once the step is accepted.

        Each iteration:

        - makes ``b`` the bound with the smaller ``|f|``;
        - ends the solve if the stopping criterion holds;
        - chooses the step ``d`` and evaluates ``b + d``;
        - keeps the bound on the other side of the root as ``c``.
        """
        interval = state.interval
        a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb
        t = 0.5 * (state.xtol - 6.0 * FLOAT64_EPS * max(abs(a), abs(b)))
        # The Algol label "int": c becomes a, the bound on the other side of the root from b.
        c, fc = a, fa
        d = e = b - a
        while True:
            # --- the Algol label "ext" ----------
            if abs(fc) < abs(fb):
                a, b, c = b, c, b
                fa, fb, fc = fb, fc, fb
            tol = 2.0 * FLOAT64_EPS * abs(b) + t
            m = 0.5 * (c - b)
            if abs(m) <= tol or fb == 0.0:
                return b

            # --- the step d ---------------------
            if abs(e) < tol or abs(fa) <= abs(fb):
                d = e = m  # A bisection is forced.
            else:
                s = fb / fa
                if a == c:
                    # The step is a linear interpolation through b and c.
                    p = 2.0 * m * s
                    q = 1.0 - s
                else:
                    # The step is an inverse quadratic interpolation through a, b and c.
                    q = fa / fc
                    r = fb / fc
                    p = s * (2.0 * m * q * (q - r) - (b - a) * (r - 1.0))
                    q = (q - 1.0) * (r - 1.0) * (s - 1.0)
                # Make p non-negative, so that q carries the sign of the step p / q.
                if p > 0.0:
                    q = -q
                else:
                    p = -p
                # s keeps the step before the previous one, and e the previous step.
                s = e
                e = d
                # Accept the interpolation step only if it lands less than 3/4 of the way from b to c and is
                # shorter than half the step before the previous one; otherwise bisect.
                if 2.0 * p < 3.0 * m * q - abs(tol * q) and p < abs(0.5 * s * q):
                    d = p / q
                else:
                    d = e = m

            # --- the evaluation at b + d --------
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
