"""`Pegasus` implements the Pegasus method: regula falsi that scales down the value of a bound kept twice in a row."""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound

from .state import PegasusState


class Pegasus(BracketingSolver[PegasusState]):
    """`Pegasus` is regula falsi that scales down the function value of a bound that the interval keeps twice in a row.

    Like regula falsi, `Pegasus` evaluates where the chord through the points at both bounds crosses zero.

    Regula falsi stalls when the function is convex or concave on the interval: regula falsi keeps 1 bound forever,
    so the interval never shrinks below the distance from that bound to the root. The Pegasus method (Dowell and
    Jarratt, 1972) avoids the stall the way the Illinois method does: it scales down the function value of the bound
    that it keeps, by a factor:

        Illinois:  factor = 0.5
        Pegasus:   factor = f_previous / (f_previous + f_new)

    ``f_previous`` and ``f_new`` are the function values at the previous and the new iterate. They have the same sign
    whenever the factor applies, so the factor lies between 0 and 1: it is 0.5 when both have the same size, and
    closer to 1 the more the new iterate reduced ``|f|``.

    Each new iterate replaces 1 bound, and the other bound is the retained bound:

    - when a new iterate lies on the same side of the root as the previous iterate, the retained bound's function
      value is multiplied by the factor before the next chord is drawn, which moves the next iterate toward the
      retained bound;
    - each further iteration that keeps that bound multiplies its value again, by that iteration's factor;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, with its
      unscaled function value.

    Dowell and Jarratt (1972) state the Pegasus step with regula falsi's chord formula, as Ford (1997) does, so the
    Pegasus method differs from `RegulaFalsi` only in its function value at the retained bound, and from `Illinois`
    only in the factor.

    References:
        - Dowell, M. and Jarratt, P. (1972). The "Pegasus" method for computing the root of an equation. BIT 12(4),
          503-508. Its section 2 states when the retained bound's value is scaled and by what factor, and its
          section 3 the chord formula. https://doi.org/10.1007/BF01932959
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. The paper's equation 5, with ``gamma = f_i / (f_i + f_(i+1))`` from the paper's
          Table 1, is the Pegasus step.
        - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="pegasus"``; the test suite checks
          `Pegasus` against mpmath's ``Illinois``.
    """

    name = "pegasus"
    version = 1
    state_cls = PegasusState

    def _next_x(self, state: PegasusState, interval: Interval) -> float:
        """Return where the chord crosses zero, with the retained bound's value scaled as the class docstring says.

        Before computing the chord, update `PegasusState`'s own fields from the replaced bound; the new iterate is the
        previous call's return value. This update is correct only when exactly 1 new evaluation happened since the
        previous call.
        """
        # --- update the retained bound's value --
        # Until the update below, state.newest_bound and state.newest_f still describe the previous iterate.
        replaced_bound = interval.last_replaced_bound
        if replaced_bound is None:
            pass  # This is the first iteration: no bound has been kept again yet, so no value is scaled.
        else:
            new_iterate_f = interval.fa if replaced_bound is IntervalBound.LOWER else interval.fb
            if replaced_bound is state.newest_bound:
                # The new iterate replaced the previous iterate, so the retained bound was kept once more.
                previous_iterate_f = state.newest_f
                scaling_factor = previous_iterate_f / (previous_iterate_f + new_iterate_f)
                state.scaled_retained_f = scaling_factor * state.scaled_retained_f
            else:
                # The new iterate replaced the retained bound, so the previous iterate is the retained bound now.
                state.scaled_retained_f = state.newest_f
                state.newest_bound = replaced_bound
            state.newest_f = new_iterate_f

        # --- regula falsi's chord ---------------
        if state.newest_bound is IntervalBound.UPPER:
            fa, fb = state.scaled_retained_f, interval.fb
        else:
            fa, fb = interval.fa, state.scaled_retained_f
        return (interval.a * fb - interval.b * fa) / (fb - fa)
