"""`Brent` implements Brent's method: interpolation steps, with bisection when they converge too slowly."""

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.stopping import interval_root, is_interval_converged
from sunnbear._core.utils.floats import FLOAT64_EPS


class Brent(Solver):
    """`Brent` implements Brent's method, as the Algol 60 procedure ``zero`` (Brent, 1971).

    Each iteration evaluates 1 x-value, reached by 1 of 3 steps from the best estimate so far:

    - inverse quadratic interpolation through the last 3 x-values;
    - linear interpolation, a secant step, when only 2 distinct x-values are known;
    - bisection, in 2 cases:

      - forced, when the step before the previous one was shorter than the tolerance ``tol`` (defined below), or
        when the last step did not reduce ``|f|``;
      - in place of an interpolation step that:

        - does not stop at least ``tol / 2`` before the x-value 3/4 of the way from the best estimate to the other
          bound;
        - is not shorter than half the step before the previous one.

    A step shorter than the tolerance is lengthened to the tolerance, toward the bound on the other side of the root.

    The steps use these quantities of Brent's procedure:

    - ``b`` and ``c`` are the interval bounds, ``b`` the one with the smaller ``|f|``, which is the best estimate;
    - ``m = 0.5*(c - b)`` is half the signed width of the interval, from ``b`` toward ``c``;
    - ``tol = 2*macheps*|b| + t`` is the tolerance, with ``macheps`` set to `FLOAT64_EPS` and ``t`` set to ``xtol``.

    The rules of the steps guarantee that the solve converges within a bounded number of evaluations, at most about the
    square of bisection's count, whatever the function, as long as ``xtol`` exceeds ``2.5*macheps*|b|``.

    For a smaller ``xtol``, a step lengthened to ``tol`` can round onto ``c`` while the interval is still wider than
    ``2*xtol``, and the solve then evaluates ``c`` again and again until its evaluation budget is exhausted.

    `Brent` departs from the procedure ``zero``, or settles a value that the procedure leaves to its caller, in these
    places:

    - **Stopping criterion:** `Brent` and the procedure check their criteria at each pass through the procedure's
      label ``ext``:

      - `Brent` stops by the shared stopping criterion, once the interval between ``b`` and ``c`` is at most
        ``2*xtol`` wide or the function value at ``b`` or ``c`` is 0, and returns that bound, or else the interval's
        midpoint, which lies within ``xtol`` of a root;
      - the procedure stops once ``|m| <= tol`` or ``f(b) = 0``, and returns ``b``.
    - **Tolerance ``t``:** the procedure leaves ``t`` to its caller; `Brent` sets ``t = xtol``, so that ``tol``, the
      length of the shortest step, is about ``xtol``, half the shared stopping width.
    - **Machine precision:** `Brent` sets ``macheps`` to `FLOAT64_EPS`, 2^-52, the value that SciPy and Numerical
      Recipes use; Brent (1971) defines ``macheps`` as the relative machine precision, which is 2^-53 in rounded
      float64 arithmetic, and also allows a larger ``macheps``.

    The bounds ``b`` and ``c`` swap roles as the iteration proceeds, so `Brent` writes its own loop, not
    `BracketingSolver`'s.

    References:
        - Brent, R. P. (1971). An algorithm with guaranteed convergence for finding a zero of a function. The
          Computer Journal 14(4), 422-425. The paper's appendix holds the Algol 60 procedure ``zero``, which `Brent`
          follows step by step. https://doi.org/10.1093/comjnl/14.4.422
        - Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall. Its chapter 4 repeats
          the 1971 paper with the procedure ``zero``, and the test suite reproduces the rows of its Table 4.1 whose
          functions do not underflow near the root. A scan is available on the author's page:
          https://maths-people.anu.edu.au/~brent/pub/pub011.html
        - SciPy's ``scipy.optimize.brentq``, whose tolerance ``(xtol + rtol*|b|) / 2`` equals ``tol`` when SciPy's
          ``xtol`` is ``2*t`` and its ``rtol`` is ``4*macheps``; the test suite checks `Brent` against
          ``scipy.optimize.brentq``.
        - Press, W. H. et al. (2007). Numerical Recipes: The Art of Scientific Computing, 3rd edition, section 9.3.
          Cambridge University Press. Its routine ``zbrent`` takes ``macheps`` as 2^-52, as `Brent` does.
        - Third parties that publish evaluation counts of Brent's method, which the test suite reproduces:

          - Chandrupatla, T. R. (1997). A new hybrid quadratic/bisection algorithm for finding the zero of a nonlinear
            function without using derivatives. Advances in Engineering Software 28(3), 145-149. Its Table 2
            holds the column "Brent's". https://doi.org/10.1016/S0965-9978(96)00051-8
          - Alefeld, G. E., Potra, F. A. and Shi, Y. (1995). Algorithm 748: Enclosing zeros of continuous functions.
            ACM Transactions on Mathematical Software 21(3), 327-344. Its Tables II and IV to VI hold the column "BR".
            https://doi.org/10.1145/210089.210111
          - Anderson, N. and Björck, Å. (1973). A new high order method of regula falsi type for computing a root of
            an equation. BIT 13(3), 253-264. Its Examples 1 to 7 hold the column "Brent".
            https://doi.org/10.1007/BF01951936
          - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
            Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its Table 2 holds the column "Bre".
            https://doi.org/10.3390/a19050332
    """

    name = "brent"
    version = 2

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with Brent's Algol procedure
        """Run Brent's procedure until `_root_if_converged` returns a root estimate, and return that estimate.

        The variables keep the names of the Algol procedure, and comments mark where its labels ``int`` and ``ext``
        fall, so that the code can be compared with the procedure line by line. Besides ``b``, ``c``, ``m``, ``tol``
        and ``t``, which the class docstring defines:

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
        t = state.xtol
        xtol_doubled = 2.0 * state.xtol
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
            x_root = self._root_if_converged(b, fb, c, fc, m, tol, xtol_doubled)
            if x_root is not None:
                return x_root

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
                # Accept the interpolation step only if it stops at least tol / 2 before the x-value 3/4 of the way
                # from b to c, and is shorter than half the step before the previous one; otherwise bisect.
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

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _root_if_converged(
        b: float, fb: float, c: float, fc: float, m: float, tol: float, xtol_doubled: float
    ) -> float | None:
        """Return the root estimate if the solve stops at the label ``ext``, or ``None`` if it continues.

        ``m`` and ``tol`` are not used. The test suite overrides this method to apply the procedure's own stopping
        criterion, ``|m| <= tol`` or ``f(b) = 0``, where it reproduces published counts.
        """
        if is_interval_converged(b, fb, c, fc, xtol_doubled):
            return interval_root(b, fb, c, fc)
        else:
            return None
