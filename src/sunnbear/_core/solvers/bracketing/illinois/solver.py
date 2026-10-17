"""`Illinois` implements the Illinois method: regula falsi that halves the value of a bound kept twice in a row."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound

from .state import IllinoisState


class Illinois(BracketingSolver[IllinoisState]):
    """`Illinois` is regula falsi that halves the function value of a bound that the interval keeps twice in a row.

    Like regula falsi, it evaluates the zero of the chord through ``(a, f(a))`` and ``(b, f(b))``.

    Regula falsi stalls when the function is convex or concave on the interval: it keeps 1 bound forever, so the
    interval never shrinks below the distance from that bound to the root. The Illinois method (Dowell and
    Jarratt, 1971) avoids the stall. Each new iterate replaces 1 bound, and the other bound is the retained bound:

    - when a new iterate lies on the same side of the root as the previous iterate, the retained bound's function
      value is halved before the next chord is drawn, which moves the next iterate toward the retained bound;
    - each further iteration that keeps that bound halves its value again;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, at its own
      function value.

    `Illinois` computes the chord's zero as Dowell and Jarratt (1971) do, as a correction to the most recent iterate:
    ``x1 - f1 * (x1 - x0) / (f1 - f0)``, with ``x1`` the most recent iterate, ``x0`` the retained bound, and ``f0``
    the function value that `Illinois` uses at ``x0``, halved once for each iteration that kept ``x0`` again.

    In exact arithmetic, this is the x-value of the chord formula that `RegulaFalsi` computes.

    Where `Illinois` departs from the ALGOL procedure of Dowell and Jarratt (1971), or settles a detail that it leaves
    open:

    - it stops by `BracketingSolver`'s criterion, once the interval is at most ``2 * xtol`` wide, and returns the
      interval's midpoint, which lies within ``xtol`` of a root; the procedure stops once a step is at most its
      tolerance ``delta``, and returns the last chord's zero without evaluating it;
    - the procedure leaves the order of its 2 starting x-values to the caller; `Illinois` passes the upper bound as
      ``x1``, the second of them, as mpmath does.

    References:
        - Dowell, M. and Jarratt, P. (1971). A modified regula falsi method for computing the root of an
          equation. BIT 11(2), 168-174. The paper's equation 2 and its ALGOL procedure give the step formula as
          `Illinois` computes it, and the ALGOL procedure also gives the halving. The test suite reproduces the
          errors in the paper's Table 1. https://doi.org/10.1007/BF01934364
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. The paper's equation 5, with ``gamma = 0.5`` from the paper's Table 1, is the
          Illinois step, and the test suite reproduces the paper's Table 4.
        - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="illinois"``; the test suite checks
          `Illinois` against mpmath's ``Illinois``.
        - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
          performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5. Its
          Table 1 holds the column "Illinois", for runs that stop by the rule of `BracketingSolver`.
          https://doi.org/10.1145/3423597
    """

    name = "illinois"
    version = 2
    state_cls = IllinoisState

    def _next_x(self, state: IllinoisState, interval: Interval) -> float:
        """Return where the chord crosses zero, with the retained bound's value halved as the class docstring says.

        Before computing the chord, update ``state.scaled_retained_f`` and ``state.newest_bound`` from the bound
        that the previous call's returned x-value replaced. This update is correct only when exactly 1 new
        evaluation happened since the previous call.
        """
        # --- update the retained bound's value --
        replaced_bound = interval.last_replaced_bound
        if replaced_bound is None:
            pass  # This is the first iteration: no bound has been kept again yet, so no value is halved.
        elif replaced_bound is state.newest_bound:
            # The new iterate replaced the previous iterate, so the retained bound was kept once more.
            state.scaled_retained_f = 0.5 * state.scaled_retained_f
        else:
            # The new iterate replaced the retained bound, so the previous iterate is the retained bound from now on.
            state.scaled_retained_f = interval.fb if replaced_bound is IntervalBound.LOWER else interval.fa
            state.newest_bound = replaced_bound

        # --- the paper's step -------------------
        # The names are the ALGOL procedure's: x1 holds the most recent iterate, x0 the retained bound.
        if state.newest_bound is IntervalBound.UPPER:
            x0, x1, f1 = interval.a, interval.b, interval.fb
        else:
            x0, x1, f1 = interval.b, interval.a, interval.fa
        f0 = state.scaled_retained_f
        return x1 - f1 * (x1 - x0) / (f1 - f0)
