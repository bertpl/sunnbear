"""`Brent` implements Brent's method: interpolation steps, with bisection when they converge too slowly.

The rest of this docstring is the record of `Brent` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article: Brent (1971), with Brent (1973), the author's book, which repeats the article in its chapter 4 and
      holds the numerical results and the Fortran translation that the article refers to:
      - Ia - article code: the Algol 60 procedure ``zero``, printed in the appendix of Brent (1971) and again in
        section 6 of the book's chapter 4; and its Fortran translation ``ZERO``, in the book's appendix, which states
        every aspect as ``zero`` does;
      - Ib - article pseudocode: none;
      - Ic - article text: Brent (1971), sections 3 to 7, which the book's chapter 4 repeats in its section 2: the
        rules of each step, the tolerance ``2 * macheps * |b| + t`` with the definition of ``macheps``, and the bound
        on the error of the returned x-value.
    - II - authors' code:
      - none.
    - III - third party:
      - SciPy's ``scipy.optimize.brentq``, whose default relative tolerance takes ``macheps`` as 2^-52;
      - Press et al. (2007), section 9.3: the routine ``zbrent``, which takes ``macheps`` as 2^-52.
    - IV - own judgment:
      - the translation of ``xtol`` into ``t``, derived from the bound of Brent (1971) on the error of the returned
        x-value.

Source per aspect:
    Every aspect follows the Algol 60 procedure ``zero``, except:
    - PRINCIPLE-GAP (P1): Brent's text defines ``macheps`` as the relative machine precision, which is 2^-53 in
      rounded float64 arithmetic, and lets ``2 * macheps`` be increased, never decreased. P1 does not say whether a
      value that the source allows, but does not define, follows the source. The code takes `FLOAT64_EPS`, 2^-52, the
      value of SciPy and Numerical Recipes (III), which the book also passes, as 16^-13, for its Table 4.1. With 2^-53:
      - 2 tested counts would change: x^9 on [-1, 4] of Table 4.1 would take 193 evaluations, 4 more than the book's
        189, and problem 3[n=1] of Alefeld, Potra and Shi (1995) 11, 1 more than the paper's 10;
      - the twin test could not follow, because SciPy's ``brentq`` refuses a relative tolerance below ``4 * 2^-52``.
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound, as for every
      solver. ``zero`` also ends there, after the same 2 evaluations, but returns the upper bound, not the lower one,
      when f is 0 at both bounds.
    - JUDGMENT-CALL: an ``xtol`` below ``6 * macheps * max(|a0|, |b0|)`` gives a negative ``t``, which ``zero`` does
      not allow; the code keeps that ``t``, because no source covers this case. The bound of Brent (1971) on the
      error of the returned x-value then no longer applies, and once ``tol`` is negative too, only the evaluation
      budget ends the solve, as ``MAX_FEVALS``. The benchmark keeps ``xtol`` above that limit.
    - Translation of ``xtol`` (P7): ``t = (xtol - 6 * macheps * max(|a0|, |b0|)) / 2``, with ``a0`` and ``b0`` the
      initial interval bounds, so that the bound ``6 * macheps * |x| + 2 * t`` of Brent (1971) on the distance from
      the returned x-value to a root ``x`` is at most ``xtol`` for every root in the initial interval.

Validation:
    - A - authors' results:
      - used: Brent (1973), Table 4.1, the 2 rows on x^9, whose evaluation counts the test reproduces within 3. On
        [-1, 4] the reproduction is convincing (P5), because the count depends on how x^9 is computed: on macOS, 4
        forms of x^9 give 187 to 192 evaluations in float64, against the book's 189.
      - PRINCIPLE-CONFLICT (P5): on [-1, 1.1], `Brent` takes 78 evaluations on macOS against the book's 81, with each
        of the 4 forms of x^9, and also in an emulation of the book's truncating hexadecimal arithmetic. The row's test
        data names that arithmetic and the platform's ``pow`` as the cause, where P5 asks for ``UNSTATED_RUN_DETAILS``
        and an observation. Marking the row so would resolve the conflict, if P5 accepts a deviation of 3 as small.
      - not used: Table 4.1's column of errors, which `Brent` does not reproduce; its other 3 rows, whose functions
        underflow near the root in float64; and Table 4.2, which states neither its intervals nor its tolerances.
      - TBD: Brent (1973), Table 6.1, the evaluation counts of ``zero`` on 19 intervals: with ``macheps`` set to the
        book's 16^-7, a run of `Brent` matches all 19; with 2^-52, it matches 2 and takes 1 or 2 evaluations more on
        the other 17.
    - B - third-party results:
      - used, each convincing (P5):
        - Chandrupatla (1997), Table 2, the column "Brent's": all 45 evaluation counts and bisection counts, exactly;
        - Alefeld, Potra and Shi (1995), Tables IV to VI: 16 of the 17 counts exactly, the 17th not checked; and
          Table II's totals within 1 %;
        - Anderson and Björck (1973), Examples 1 to 7, in single precision: 22 of the 26 counts exactly, and the
          other 4 within 1;
        - Ganchovski et al. (2026), Table 2, the column "Bre": 90 of the 92 counts exactly, 2 within 1, and all 92
          roots;
      - not used: Alefeld, Potra and Shi (1995), Table III; the double-precision totals of Anderson and Björck (1973);
        and Gao (2026), Tables 1 and 3 and its columns "Brenth". The docstring of the test package
        ``tests.solvers.bracketing.brent`` gives the reasons.
      - TBD: Oliveira and Takahashi (2020), Table 1, the column "Matlab", whose counts are those of MATLAB's
        ``fzero``, a descendant of ``zero``: with ``t = 2e-10``, twice the paper's tolerance, 23 of the 24 counts
        match, and the 24th lies 1 lower.
      - TBD: Gao (2026), Tables 2 and 4, the columns "Brentq", whose counts are those of SciPy's ``brentq``: with
        SciPy's ``xtol = 1e-10``, `Brent` matches both counts of Table 2 and 35 of the 45 of Table 4. On x^19 it takes
        10 to 13 evaluations more, because ``brentq`` computes the inverse quadratic step from divided differences,
        and the product in its denominator underflows to 0 there, so that ``brentq`` bisects.
    - C - reference implementation:
      - used: a twin test checks that `Brent` evaluates the same x-values as SciPy's ``scipy.optimize.brentq``; the
        twin test imposes the stopping rule of `Brent` on SciPy.

Variants:
    - `BrentConfig`, the only config, is core (P8).
"""

from sunnbear._core.solvers.core import Solver, SolveState
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
    As long as ``tol`` stays positive, these rules guarantee that the solve converges within a bounded number of
    evaluations, at most about the square of bisection's count, whatever the function.

    The stopping criterion and the tolerance use these quantities of Brent's procedure:

    - ``b`` and ``c`` are the interval bounds, ``b`` the one with the smaller ``|f|``, which is the best estimate;
    - ``m`` is half the signed width of the interval, from ``b`` toward ``c``;
    - ``tol = 2 * macheps * |b| + t`` is the tolerance, with ``macheps`` set to `FLOAT64_EPS`, 2^-52, and ``t`` an
      absolute tolerance derived from ``xtol`` (below); the solve ends once ``|m| <= tol`` or ``f(b) = 0``, and
      returns ``b``.

    Brent's procedure returns a ``b`` within ``6 * macheps * |x| + 2 * t`` of a root ``x``, up to the terms of order
    ``macheps * t`` and ``macheps^2 * |x|`` that Brent (1971) neglects. The solver sets
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
        - Brent, R. P. (1973). Algorithms for Minimization without Derivatives. Prentice-Hall. Its chapter 4 repeats
          the 1971 paper with the procedure ``zero``, and its appendix holds the Fortran translation ``ZERO``. The test
          suite reproduces the rows of its Table 4.1 whose functions do not underflow near the root; its Table 6.1, in
          chapter 5, also gives evaluation counts of ``zero``. The author offers a scan of the book on
          https://maths-people.anu.edu.au/~brent/pub/pub011.html.
        - SciPy's ``scipy.optimize.brentq``, whose tolerance ``(xtol + rtol * |b|) / 2`` equals ``tol`` when SciPy's
          ``xtol`` is ``2 * t`` and its ``rtol`` is ``4 * macheps``; the test suite checks `Brent` against
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
        - Third parties that publish evaluation counts of other implementations of Brent's method, which the test
          suite does not check yet:

          - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
            performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5. Its
            Table 1 holds the column "Matlab", for MATLAB's ``fzero``. https://doi.org/10.1145/3423597
          - Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics
            Letters 178, 109928. Its Tables 2 and 4 hold the columns "Brentq", for SciPy's ``brentq``.
            https://doi.org/10.1016/j.aml.2026.109928
    """

    name = "brent"
    version = 1

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with Brent's Algol procedure
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
