"""`Ellithy` implements the 4 methods of Ellithy (2026): bisection or trisection, false position, modified secant."""

from sunnbear._core.solvers.core import Interval, IntervalBound, Solver, SolveState

from .variant import EllithyVariant

# `_ZERO_DENOMINATOR_GUARD` is the article's `eps`, its guard against a zero denominator in the modified-secant step:
# where the denominator is exactly 0, the step adds `_ZERO_DENOMINATOR_GUARD` to it.
_ZERO_DENOMINATOR_GUARD = 1e-15


class Ellithy(Solver):
    """`Ellithy` implements the 4 multi-phase hybrid bracketing methods of Ellithy (2026), in 4 variants.

    The article presents its 4 methods as settings of 1 design: each iteration runs up to 3 phases on the interval
    ``[a, b]``, with ``fa = f(a)`` and ``fb = f(b)``, and each phase works on the previous phase's interval:

    - **phase 1, bisection or trisection:** bisection evaluates the midpoint ``x_B = 0.5*(a + b)`` and splits the
      interval there. Trisection evaluates both ``x1 = a + (b - a)/3`` and ``x2 = b - (b - a)/3`` before it updates
      the interval, which becomes:

      - ``[a, x1]`` where ``f(x1)`` differs in sign from ``fa``;
      - else ``[x1, x2]`` where ``f(x2)`` differs in sign from ``f(x1)``;
      - else ``[x2, b]``;
    - **phase 2, false position:** the article's equation 1 gives ``x_FP = (a*fb - b*fa) / (fb - fa)``, which is
      evaluated and splits the interval;
    - **phase 3, modified secant:** the article's equation 2, a secant step from ``x_FP`` over a finite-difference
      step ``delta``:

          x_S = x_FP - (delta*f(x_FP)) / (f(x_FP + delta) - f(x_FP)),  with  delta = 1e-8*max(1, |x_FP|) + 1e-15

      The step needs 1 evaluation at ``x_FP + delta``, the probe. Where the denominator is exactly 0, the step adds
      ``eps = 1e-15`` to it. ``x_S`` is evaluated only if it lies strictly inside the interval, and splits the interval
      only if ``|f(x_S)| < |f(x_FP)|``; the probe and a rejected ``x_S`` never change the interval.

    ``variant``, a value of `EllithyVariant`, picks the method:

        "bf":    Opt.BF, the article's Algorithm 1: bisection, then false position
        "bfms":  Opt.BFMS, the article's Algorithm 2: bisection, false position, then modified secant
        "tf":    Opt.TF, the article's Algorithm 3: trisection, then false position
        "tfms":  Opt.TFMS, the article's Algorithm 4: trisection, false position, then modified secant

    A complete iteration evaluates the function:

    - 2 times in ``"bf"``;
    - 3 times in ``"tf"``;
    - 3 or 4 times in ``"bfms"``;
    - 4 or 5 times in ``"tfms"``.

    The shared stopping criterion of the bracketing solvers ends the solve once the interval is at most ``2*xtol``
    wide, or once the function value at an interval bound is exactly 0. It returns that bound, or else the interval's
    midpoint, which then lies within ``xtol`` of a root. As in the article, there is no check before the first
    iteration.

    `Ellithy` checks this criterion at each point where the article tests its own stopping criterion, ``|f(x)| <= tol``,
    after the interval update of that phase:

    - ``"bf"``: after the bisection, and after the false position;
    - ``"bfms"``: after the false position, and after an accepted ``x_S``. Algorithm 2 has no test after its bisection,
      while Algorithm 1 has one; `Ellithy` follows each algorithm as printed;
    - ``"tf"``: after the trisection, and after the false position;
    - ``"tfms"``: after the trisection, after the false position, and after an accepted ``x_S``.

    `Ellithy` departs from Ellithy (2026) in these places:

    - **Stopping criterion:** `Ellithy` stops by the shared stopping criterion above. The article's pseudocode tests
      ``|f(x)| <= tol`` at the points that the list above names, and returns that ``x``, or returns the interval's
      midpoint after ``max_iter`` iterations.

      ``xtol`` is a tolerance on x and cannot express a tolerance on ``|f(x)|``, and `Ellithy` has no iteration limit,
      so the evaluation budget ends a long solve.

      The article's section 5.2 states a different criterion, ``|b - a| < 1e-14`` and ``|f(x)| < 1e-14``. The
      pseudocode and the authors' code test ``|f(x)|`` alone.
    - **Sign tests:** the article tests the sign of a product, such as ``fa*f(x_B) < 0``; the product of 2 small
      function values can underflow to 0, so `Ellithy` compares the signs directly, with `Interval.split_at`.
    - **A zero at** ``x1``: where ``f(x1) = 0``, the article's trisection update would move ``a`` to ``x2`` and lose
      that zero, but the article's test ``|f(x1)| <= tol`` has already returned ``x1``. `Ellithy` keeps ``x1`` as the
      lower bound, so the shared stopping criterion ends the solve at ``x1``.
    - **A zero at** ``x2`` **outside the new interval:** where ``f(x2) = 0`` but the trisection update keeps
      ``[a, x1]``, which holds a sign change too, the article's test ``|f(x2)| <= tol`` returns ``x2``. The shared
      stopping criterion reads only the interval bounds, so `Ellithy` continues on ``[a, x1]`` to a root there.
    - **The probe, evaluated once:** where the denominator of the modified-secant step is 0, the article evaluates
      ``f(x_FP + delta)`` a second time; `Ellithy` reuses the value of the first evaluation.
    - **Guards against a zero denominator:** the article adds ``eps`` to a denominator where its division raises an
      error. A float division in Python raises only for a denominator of 0, so `Ellithy` adds ``eps`` only there.

      The article also guards the false position, whose denominator ``fb - fa`` is never 0, because ``fa`` and ``fb``
      differ in sign; `Ellithy` leaves that guard out.

    A known caveat: where ``x_FP`` lies within ``delta`` of the upper bound of the initial interval, the probe
    ``x_FP + delta`` lies outside the initial interval. `Ellithy` keeps the probe as printed. Where the function cannot
    be evaluated at the probe, `Solver.solve` records the solve as ``DIVERGED``, because the evaluation failed outside
    the interval.

    The bracketing solvers derive from ``xtol`` any margin that keeps a new x-value away from the interval bounds.
    ``delta`` is no such margin: it is a finite-difference step that estimates the derivative at ``x_FP``, so `Ellithy`
    keeps its printed value, as it keeps the guard ``eps``.

    An iteration evaluates the function several times, so `Ellithy` writes its own loop, not `BracketingSolver`'s.

    References:
        - Ellithy, A. (2026). Four new multi-phase hybrid bracketing algorithms for numerical root finding. Journal of
          the Egyptian Mathematical Society 34(1), 91-115:

          - its Algorithms 1 to 4 are the 4 variants, and its equations 1 and 2 the false position and the
            modified-secant step;
          - the test suite reproduces the iteration counts of its Tables 2 to 5 and 12, and the statistics of the
            iteration counts in its Table 7.

          https://doi.org/10.21608/joems.2026.440115.1078
        - The authors' code, at commit ``7f22131ef4e1def3e3928dc6558f46f756d0a5ea`` (MIT license). Its experiment
          scripts follow Algorithms 1 to 4 line by line.
          https://github.com/Abdelrhman-Ellithy/hybridroots
        - The package ``hybridroots``, the authors' implementation of the 4 methods; the test suite checks `Ellithy`
          against version 1.0.1. https://pypi.org/project/hybridroots/
    """

    name = "ellithy"
    version = 1

    # These are the 2 constants of the article's step delta = _DELTA_FACTOR * max(1, |x_FP|) + _DELTA_OFFSET. They are
    # class attributes, so that the test suite can set a fixed delta in a subclass: some counts of Opt.BFMS and Opt.TFMS
    # in the article's Table 12 reproduce only with a fixed delta.
    _DELTA_FACTOR = 1e-8
    _DELTA_OFFSET = 1e-15

    def __init__(self, *, variant: EllithyVariant) -> None:
        """Configure the variant, which may also be given as a plain string; the class docstring describes each variant.

        Raises:
            ValueError: If ``variant`` is not a value of `EllithyVariant`.
        """
        self.variant = EllithyVariant(variant)

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with Algorithms 1 to 4
        """Run the variant's iterations until `_root_if_converged` returns a root estimate, and return that estimate.

        Each iteration runs the variant's phases, as the class docstring describes, and calls `_root_if_converged` at
        each point where the article tests its own stopping criterion. The variable names follow the article's, spelled
        as Python identifiers: ``x_b`` is its ``x_B``, ``x_fp`` its ``x_FP`` and ``x_s`` its ``x_S``; ``n`` counts the
        iterations from 1, as the article does.
        """
        interval = state.interval
        xtol_doubled = 2.0 * state.xtol
        has_bisection_step = self.variant.has_bisection_step
        has_secant_step = self.variant.has_secant_step
        n = 0
        while True:
            n += 1
            if has_bisection_step:
                # --- phase 1: bisection ---------
                x_b = interval.midpoint
                fx_b = state.f(x_b)
                state.x_best = x_b
                interval = interval.split_at(x_b, fx_b)
                if self.variant is EllithyVariant.BF:  # Algorithm 2, of "bfms", has no test after its bisection.
                    x_root = self._root_if_converged(interval, xtol_doubled, n, ((x_b, fx_b),))
                    if x_root is not None:
                        return x_root
            else:
                # --- phase 1: trisection --------
                # Algorithm 3 computes (b - a)/3 twice and Algorithm 4 once; both give the same x-values.
                third = interval.width / 3.0
                x1 = interval.a + third
                x2 = interval.b - third
                fx1 = state.f(x1)
                state.x_best = x1
                fx2 = state.f(x2)
                state.x_best = x2
                interval = interval.split_at(x1, fx1)
                # x2 lies inside the interval only if x1 replaced the lower bound; a zero at x1 must stay a bound, as
                # the class docstring says.
                if interval.last_replaced_bound is IntervalBound.LOWER and not interval.is_fa_zero:
                    interval = interval.split_at(x2, fx2)
                x_root = self._root_if_converged(interval, xtol_doubled, n, ((x1, fx1), (x2, fx2)))
                if x_root is not None:
                    return x_root

            # --- phase 2: false position --------
            a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb
            x_fp = (a * fb - b * fa) / (fb - fa)
            fx_fp = state.f(x_fp)
            state.x_best = x_fp
            interval = interval.split_at(x_fp, fx_fp)
            x_root = self._root_if_converged(interval, xtol_doubled, n, ((x_fp, fx_fp),))
            if x_root is not None:
                return x_root

            # --- phase 3: modified secant -------
            if has_secant_step:
                # Where |x_fp| <= 1, max returns the plain float 1.0, not a flop-counted value, so delta is a plain
                # constant and its 2 operations add no flops to the count.
                delta = self._DELTA_FACTOR * max(1.0, abs(x_fp)) + self._DELTA_OFFSET
                # The probe and a rejected x_s are not estimates of the root, so they leave state.x_best unchanged.
                f_probe = state.f(x_fp + delta)
                try:
                    x_s = x_fp - (delta * fx_fp) / (f_probe - fx_fp)
                except ZeroDivisionError:
                    x_s = x_fp - (delta * fx_fp) / ((f_probe - fx_fp) + _ZERO_DENOMINATOR_GUARD)
                if interval.a < x_s < interval.b:
                    fx_s = state.f(x_s)
                    if abs(fx_s) < abs(fx_fp):
                        state.x_best = x_s
                        interval = interval.split_at(x_s, fx_s)
                        x_root = self._root_if_converged(interval, xtol_doubled, n, ((x_s, fx_s),))
                        if x_root is not None:
                            return x_root

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _root_if_converged(
        interval: Interval,
        xtol_doubled: float,
        iteration_number: int,
        evaluations_tested_by_article: tuple[tuple[float, float], ...],
    ) -> float | None:
        """Return the root estimate if the solve ends at ``interval``, or ``None`` if it continues.

        ``iteration_number`` is the iteration's number, and ``evaluations_tested_by_article`` holds the ``(x, f(x))``
        pairs whose ``|f(x)|`` the article tests at this point. Neither is used here: the test suite reproduces the
        article's published iteration counts with a subclass that overrides this method with the article's own stopping
        criterion, which needs both.
        """
        if interval.is_converged(xtol_doubled):
            return interval.root()
        else:
            return None
