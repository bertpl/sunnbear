"""`Pegasus` implements the Pegasus method: regula falsi that scales down the value of a bound kept twice in a row.

The rest of this docstring is the record of `Pegasus` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - Ia - article code: none;
      - Ib - article pseudocode: none;
      - Ic - article text: Dowell and Jarratt (1972), sections 1 to 3: the rules that scale the function value of a
        bound kept twice in a row, and the formula of the chord's zero.
    - II - authors' code:
      - none.
    - III - third party:
      - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="pegasus"``;
      - Ford (1997), equation 5, with the factor of its Table 1.
    - IV - own judgment:
      - none.

Source per aspect:
    Every aspect follows Dowell and Jarratt (1972), except:
    - `Pegasus` takes the upper bound as the newer starting x-value, ``x_1``, as mpmath does, because the article
      leaves the order of ``x_0`` and ``x_1`` to the caller.
    - PRINCIPLE-GAP (P6): the article writes the retained bound's scaled value in 2 forms, and P6 does not say which
      written form counts:
      - in its formula, as ``f_(i-1) * f_i / (f_i + f_(i+1))``;
      - in its prose, as ``f_(i-1)`` scaled by the factor ``f_i / (f_i + f_(i+1))``, the form of mpmath and Ford.
      The code multiplies first, as the formula is printed, so the product of 2 function values overflows or
      underflows when f is scaled by about 1e154 or 1e-165; at those scales, the factor form still converges.
    - PRINCIPLE-GAP (P7): the article stops its runs once ``|f(x)|`` falls below a threshold, and P7 does not say how
      ``xtol``, a tolerance on x, translates into one on f. The code stops by `BracketingSolver`'s rule instead: once
      the interval is at most ``2 * xtol`` wide, it returns the interval's midpoint.

Validation:
    - A - authors' results:
      - used: Table 1, the errors of ``x_2`` to ``x_7``, reproduced to the printed digits, which is convincing (P5);
      - not used: Table 1's ``x_8`` and ``x_9``, and the iteration counts of Problems 1 to 4; the docstring of the
        test package ``tests.solvers.bracketing.pegasus`` gives the reasons.
    - B - third-party results:
      - used: Ford (1997), Table 4, reproduced to within 1 iteration, which is convincing (P5);
      - not used: Anderson and Björck (1973), Examples 1 to 7, the Pegasus columns; the docstring of the test package
        ``tests.solvers.bracketing.anderson_bjorck`` gives the reasons.
    - C - reference implementation:
      - used: a twin test checks that `Pegasus` evaluates the same x-values as mpmath's ``Illinois`` with
        ``method="pegasus"``; the twin test imposes the stopping rule of `Pegasus` on mpmath.

Variants:
    - `PegasusConfig`, the only config, is secondary (P8); this record marks no PRINCIPLE-CONFLICT.
"""

from sunnbear._core.solvers.core import BracketingSolver, Interval, IntervalBound

from .state import PegasusState


class Pegasus(BracketingSolver[PegasusState]):
    """`Pegasus` is regula falsi that scales down the function value of a bound that the interval keeps twice in a row.

    Like regula falsi, `Pegasus` evaluates the zero of the chord through ``(a, f(a))`` and ``(b, f(b))``.

    Regula falsi stalls when the function is convex or concave on the interval: regula falsi keeps 1 bound forever,
    so the interval never shrinks below the distance from that bound to the root. The Pegasus method (Dowell and
    Jarratt, 1972) avoids the stall the way the Illinois method does: it scales down the function value of the bound
    that it keeps, by a factor:

        Illinois:  factor = 0.5
        Pegasus:   factor = f_previous / (f_previous + f_new)

    ``f_previous`` and ``f_new`` are the function values at the previous and the new iterate. They have the same sign
    whenever the factor applies, so the factor lies between 0 and 1: it is 0.5 when both have the same size, and
    closer to 1 the more the new iterate reduced ``|f|``.

    `Pegasus` scales in the order of section 2 of Dowell and Jarratt (1972): it multiplies the retained bound's value
    by ``f_previous`` first, then divides by ``f_previous + f_new``.

    Each new iterate replaces 1 bound, and the other bound is the retained bound:

    - when a new iterate lies on the same side of the root as the previous iterate, the retained bound's function
      value is multiplied by the factor before the next chord is drawn, which moves the next iterate toward the
      retained bound;
    - each further iteration that keeps that bound multiplies its value again, by that iteration's factor;
    - when a new iterate replaces the retained bound, the previous iterate becomes the retained bound, with its
      unscaled function value.

    Dowell and Jarratt (1972) state the Pegasus step with regula falsi's chord formula, as Ford (1997) does, so the
    Pegasus method differs from regula falsi only in its function value at the retained bound, and from the Illinois
    method only in the factor.

    `Illinois` computes the same zero of the chord, in the form of Dowell and Jarratt (1971).

    `Pegasus` stops by `BracketingSolver`'s criterion, so the returned x-value lies within ``xtol`` of a root.

    References:
        - Dowell, M. and Jarratt, P. (1972). The "Pegasus" method for computing the root of an equation. BIT 12(4),
          503-508. Its section 2 states when the retained bound's value is scaled and by what factor, and its
          section 3 the chord formula. The test suite reproduces the errors in the paper's Table 1.
          https://doi.org/10.1007/BF01932959
        - Ford, J. A. (1997). Improved Illinois-type methods for the solution of nonlinear equations. Scientia
          Iranica 4(1&2), 28-34. The paper's equation 5, with ``gamma = f_i / (f_i + f_(i+1))`` from the paper's
          Table 1, is the Pegasus step, and the test suite reproduces the paper's Table 4.
        - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="pegasus"``; the test suite checks
          `Pegasus` against mpmath's ``Illinois``.
        - Anderson, N. and Björck, Å. (1973). A new high order method of regula falsi type for computing a root of an
          equation. BIT 13(3), 253-264. Its examples 1 to 7 hold columns for the Pegasus method, which the test suite
          does not reproduce. https://doi.org/10.1007/BF01951936
    """

    name = "pegasus"
    version = 2
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
                state.scaled_retained_f = (
                    state.scaled_retained_f * previous_iterate_f / (previous_iterate_f + new_iterate_f)
                )
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
