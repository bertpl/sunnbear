"""`Illinois` implements the Illinois method: regula falsi that halves the value of a bound kept twice in a row."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound

from .state import IllinoisState


class Illinois(BracketingSolver[IllinoisState]):
    """`Illinois` is regula falsi that halves the function value of a bound that the interval keeps twice in a row.

    Like regula falsi, it evaluates where the chord through the bound points crosses zero.

    Regula falsi stalls when the function is convex or concave on the interval: it keeps 1 bound forever, so the
    interval never shrinks below the distance from that bound to the root. The Illinois method (Dowell and
    Jarratt, 1971) avoids the stall. Each new iterate replaces 1 bound, and the other bound is the retained bound:

    - when a new iterate lies on the same side of the root as the previous iterate, the retained bound's function
      value is halved before the next chord is drawn, which moves the next iterate toward the retained bound;
    - each further iteration that keeps that bound halves its value again;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, at its own
      function value.

    Ford (1997) states the Illinois step with regula falsi's chord formula, so the Illinois method differs from
    `RegulaFalsi` only in its function value at the retained bound.

    References:
        - Dowell, M. and Jarratt, P. (1971). A modified regula falsi method for computing the root of an
          equation. BIT 11(2), 168-174. https://doi.org/10.1007/BF01934364
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. The paper's equation 5, with ``gamma = 0.5`` from the paper's Table 1, is the
          Illinois step.
        - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="illinois"``; the test suite checks
          `Illinois` against mpmath's ``Illinois``.
    """

    name = "illinois"
    version = 1
    state_cls = IllinoisState

    def _next_x(self, state: IllinoisState, interval: Interval) -> float:
        """Return where the chord crosses zero, with the retained bound's value halved as the class docstring says.

        Before computing the chord, update ``state.scaled_retained_f`` and ``state.newest_bound`` from the bound
        that the previous iterate replaced. This update is correct only when exactly 1 new evaluation happened
        since the previous call.
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

        # --- regula falsi's chord ---------------
        if state.newest_bound is IntervalBound.UPPER:
            fa, fb = state.scaled_retained_f, interval.fb
        else:
            fa, fb = interval.fa, state.scaled_retained_f
        return (interval.a * fb - interval.b * fa) / (fb - fa)
