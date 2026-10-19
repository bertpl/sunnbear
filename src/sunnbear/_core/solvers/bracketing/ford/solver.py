"""`Ford` implements 3 methods of Ford (1997): regula falsi that scales down the value of a bound kept twice in a row."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound

from .state import FordState
from .variant import FordVariant


class Ford(BracketingSolver[FordState]):
    """`Ford` is regula falsi that scales down the function value of a bound that the interval keeps twice in a row.

    `Ford` implements Methods 1, 3 and 4 of Ford (1997), in 3 variants.

    Like regula falsi, `Ford` evaluates the zero of the secant through the 2 interval bounds. Ford writes that zero as
    ``(s*f(r) - r*f(s)) / (f(r) - f(s))``, where ``s`` is the most recent iterate and ``r`` the other interval bound,
    the retained bound.

    Regula falsi stalls when the function is convex or concave on the interval: regula falsi keeps 1 bound forever, so
    the interval never shrinks below the distance from that bound to the root. Ford's methods avoid the stall the way
    the Illinois, Pegasus and Anderson-Björck methods do. Each new iterate replaces 1 bound:

    - when a new iterate ``x_(i+1)`` lies on the same side of the root as the previous iterate ``x_i``, the function
      value at the retained bound ``x_(i-1)`` is multiplied by a factor ``gamma`` before the next secant is drawn,
      which moves the next iterate toward the retained bound;
    - each further iteration that keeps that bound multiplies its value again, by that iteration's ``gamma``;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, with its
      unscaled function value.

    The article calls a step whose secant uses a scaled function value modified, and any other step unmodified.

    The factor that makes the next secant pass through the root ``x*`` is the ratio of 2 slopes,
    ``f[x_(i+1), x*] / f[x_(i-1), x*]``, where ``f[u, v] = (f(u) - f(v)) / (u - v)`` is the divided difference. Each
    method approximates both slopes with divided differences between ``x_(i-1)``, ``x_i`` and ``x_(i+1)``, and takes
    their ratio as ``gamma``. All 3 methods approximate the numerator by the slope at ``x_(i+1)`` of the quadratic
    through the function values at the 3 x-values,

        f[x_(i+1), x_i] + f[x_(i+1), x_(i-1)] - f[x_i, x_(i-1)],

    and differ only in the denominator, which ``variant``, a value of `FordVariant`, picks from the article's Table 3:

        "method_1":  f[x_(i-1), x_(i+1)] + f[x_(i-1), x_i] - f[x_(i+1), x_i], the quadratic's slope at x_(i-1)
        "method_3":  f[x_(i-1), x_(i+1)]
        "method_4":  f[x_(i-1), x_i]

    Where ``gamma`` is not positive, all 3 methods take ``gamma = 0.5``, the Illinois method's factor.

    The article's description of the steps leaves out 2 details, which its analysis of a second modified step in a
    row, in its equations 23 to 25, shows: the divided differences use the scaled function value at ``x_(i-1)``, and
    each further iteration that keeps the retained bound scales that scaled value again.

    `Ford` computes every step in the form of the article's equation 5, ``(s*fr - r*fs) / (fr - fs)``, with
    ``fs = f(s)``, and ``fr`` the scaled or unscaled function value at ``r``. The article gives the unmodified step in
    2 forms, its equations 2 and 3, and calls a step with equation 3 unmodified; equation 5 is equation 3 with the
    scaled value.

    Ford's Method 2 is left out: Ford finds that it behaves very much like the Anderson-Björck method, which
    `AndersonBjorck` implements, and drops it from the article's discussion.

    `Ford` departs from Ford (1997), or settles a detail that the article leaves open, in these places:

    - **Stopping criterion:** `Ford` stops by `BracketingSolver`'s criterion, once the interval is at most ``2*xtol``
      wide or the function value at a bound is 0, and returns that bound, or else the interval's midpoint, which lies
      within ``xtol`` of a root. The article's experiments stop once ``|f(x)| < eps``, or once the interval is narrower
      than ``0.95*eps``, with ``eps = tau + 2^-53*max(|a|, |b|, 1)`` for a tolerance ``tau`` and the initial interval
      ``[a, b]``, or after 200 iterations. The test on ``|f(x)|`` is a tolerance on f that ``xtol``, a tolerance on x,
      does not translate into; `Ford` has no iteration limit, so the evaluation budget ends a long solve.
    - **Fallback condition:** the article takes ``gamma = 0.5`` where ``gamma`` is "non-negative" (pp. 29 and 30), a
      typo for "non-positive": only with that reading do the counts of the article's Table 4 reproduce. `Ford` takes
      0.5 where ``gamma`` is not positive.
    - **Starting order:** the article leaves open which bound of the initial interval is the first ``s``, the most
      recent iterate; `Ford` takes the upper bound, as `Illinois`, `Pegasus` and `AndersonBjorck` do, and with that
      order the counts of the article's Table 4 reproduce.
    - **Side of the root:** the article tests whether a new iterate lies on the other side of the root by the sign of
      ``f_(i+1)*f_i``; the product of 2 small function values can underflow to 0, so `Ford` splits the interval by the
      sign of ``f_(i+1)`` alone, with `Interval.split_at`.
    - **Division by 0:** `Ford` takes ``gamma = 0.5`` where ``x_(i+1)`` equals ``x_i``, so that ``f[x_(i+1), x_i]``
      would be ``0/0``, and where the denominator of ``gamma`` is exactly 0; Method 1's denominator can round to 0.
      Both tests only keep Python from raising a ``ZeroDivisionError``; the article has neither. ``x_(i+1)`` can equal
      ``x_i`` where ``xtol`` lies below half the float spacing near the root, as at ``xtol = 0``.

    References:
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. Its equations 3 and 5 are the steps, its Table 3 the approximations of the 2 slopes
          of ``gamma``, and its equations 23 to 25 the repeated scaling; the test suite reproduces the iteration
          counts of Methods 1, 3 and 4 in its Table 4. https://scientiairanica.sharif.edu/article_21758.html
        - Anderson, N. and Björck, Å. (1973). A new high order method of regula falsi type for computing a root of an
          equation. BIT 13(3), 253-264. Its section 3 takes 0.5 in place of a factor that is not positive, the
          reading of Ford's fallback that `Ford` follows. https://doi.org/10.1007/BF01951936
    """

    name = "ford"
    version = 1
    state_cls = FordState

    def __init__(self, *, variant: FordVariant) -> None:
        """Configure the variant, which may also be given as a plain string; the class docstring describes each variant.

        Raises:
            ValueError: If ``variant`` is not a value of `FordVariant`.
        """
        self.variant = FordVariant(variant)

    def _next_x(self, state: FordState, interval: Interval) -> float:
        """Return the secant's zero, with the retained bound's value scaled as the class docstring says.

        Before computing the secant, update `FordState`'s own fields from the replaced bound; the new iterate is the
        previous call's return value. This update is correct only when exactly 1 new evaluation happened since the
        previous call.
        """
        # --- update the retained bound's value --
        # The names are the article's: x_ip1, x_i and x_im1 stand for x_(i+1), the new iterate, x_i, the previous
        # iterate, and x_(i-1), the retained bound; f_ip1, f_i and f_im1 are the function values there, with f_im1
        # the retained bound's scaled value.
        replaced_bound = interval.last_replaced_bound
        if replaced_bound is None:
            pass  # This is the first iteration: no bound has been kept again yet, so no value is scaled.
        else:
            if replaced_bound is IntervalBound.LOWER:
                x_ip1, f_ip1, x_im1 = interval.a, interval.fa, interval.b
            else:
                x_ip1, f_ip1, x_im1 = interval.b, interval.fb, interval.a
            x_i, f_i, f_im1 = state.newest_x, state.newest_f, state.scaled_retained_f
            if replaced_bound is not state.newest_bound:
                # x_(i+1) replaced the retained bound, on the other side of the root from x_i, so x_i becomes the
                # retained bound, with its unscaled function value f_i, and the next step is unmodified.
                state.scaled_retained_f = f_i
                state.newest_bound = replaced_bound
            elif x_ip1 == x_i:
                # f[x_(i+1), x_i] would be 0/0. Taking 0.5 only avoids Python's ZeroDivisionError, as the class
                # docstring says; in IEEE arithmetic, 0/0 is NaN, which is not positive either.
                state.scaled_retained_f = 0.5 * f_im1
            else:
                # x_(i+1) replaced x_i, so the retained bound was kept once more, and its value is scaled by gamma.
                # slope_ip1_i is the divided difference f[x_(i+1), x_i], and likewise for the other 2.
                slope_ip1_i = (f_ip1 - f_i) / (x_ip1 - x_i)
                slope_ip1_im1 = (f_ip1 - f_im1) / (x_ip1 - x_im1)
                slope_i_im1 = (f_i - f_im1) / (x_i - x_im1)
                numerator = slope_ip1_i + slope_ip1_im1 - slope_i_im1
                # f[u, v] and f[v, u] are equal bit for bit, because they differ only by negations, which are exact,
                # so Method 1's denominator reuses the 3 divided differences of the numerator.
                if self.variant is FordVariant.METHOD_1:
                    denominator = slope_ip1_im1 + slope_i_im1 - slope_ip1_i
                elif self.variant is FordVariant.METHOD_3:
                    denominator = slope_ip1_im1
                else:  # FordVariant.METHOD_4
                    denominator = slope_i_im1
                if denominator == 0.0:
                    # Taking 0.5 only avoids Python's ZeroDivisionError, as the class docstring says.
                    gamma = 0.5
                else:
                    gamma = numerator / denominator
                if gamma > 0.0:
                    state.scaled_retained_f = gamma * f_im1
                else:
                    # The article's fallback, for a gamma that is not positive, as the class docstring says.
                    state.scaled_retained_f = 0.5 * f_im1
            state.newest_x, state.newest_f = x_ip1, f_ip1

        # --- the article's equation 5 -----------
        if state.newest_bound is IntervalBound.UPPER:
            r, s, fs = interval.a, interval.b, interval.fb
        else:
            r, s, fs = interval.b, interval.a, interval.fa
        fr = state.scaled_retained_f
        return (s * fr - r * fs) / (fr - fs)
