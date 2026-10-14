"""`Illinois` implements the Illinois method: regula falsi that halves the value of a bound kept twice in a row.

The rest of this docstring is the record of `Illinois` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

Sources:
    - I - article:
      - Ia - article code: Dowell and Jarratt (1971), the ALGOL procedure in its section 4;
      - Ib - article pseudocode: none;
      - Ic - article text: Dowell and Jarratt (1971), its equation 2 and the rules of its section 2.
    - II - authors' code:
      - none.
    - III - third party:
      - mpmath's ``mpmath.calculus.optimization.Illinois``, with ``method="illinois"``;
      - Ford (1997), equation 5, with the factor 0.5 of its Table 1.
    - IV - own judgment:
      - none.

Source per aspect:
    Every aspect follows the ALGOL procedure of Dowell and Jarratt (1971), except:
    - `Illinois` passes the upper bound as ``x1``, the second of the 2 starting x-values, as mpmath does, because the
      ALGOL procedure leaves the order of ``x0`` and ``x1`` to the caller.
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound, as for every
      solver. When the function value is 0 at the lower bound, the ALGOL procedure first evaluates the zero of the chord
      through the 2 bounds, which lies at that bound up to rounding.
    - PRINCIPLE-GAP (P6): Dowell and Jarratt's Table 1 gives the same digits with either of 2 forms of the chord's zero:
      - the ALGOL procedure's form, ``x1 - f1 * (x1 - x0) / (f1 - f0)``, with ``x1`` the most recent iterate and ``x0``
        the retained bound;
      - Ford's form, ``(a * fb - b * fa) / (fb - fa)``, with ``fa`` and ``fb`` the function values at the interval
        bounds ``a`` and ``b``.
      P6 does not say whether third-party tables may decide between the 2 forms. The code keeps the ALGOL form, the
      form of the record's default source, because the 2 third-party tables disagree on which form they match:
      - with the ALGOL form, all 15 counts of Ford's Table 4 match within 1, against 14 with Ford's form;
      - with Ford's form, 22 of the 24 counts in the column "Illinois" of Table 1 of Oliveira and Takahashi (2020)
        match exactly, against 17 with the ALGOL form.
    - PRINCIPLE-CONFLICT (P1): the code stops by `BracketingSolver`'s rule, once the interval is at most ``2 * xtol``
      wide, and returns the interval's midpoint. The ALGOL procedure stops once a step is at most ``delta``, and
      returns the last chord's zero without evaluating it. Either of 2 changes would resolve the conflict:
      - following the ALGOL procedure with ``delta = xtol``; on 132 solves of the test suite's problems, that stopping
        rule returns an x-value that is not within ``xtol`` of a root in 22 of them;
      - a principle that lets a solver use `BracketingSolver`'s rule in place of its source's rule when the source's
        rule does not guarantee an x-value within ``xtol`` of a root.
    - Translation of ``xtol`` (P7): ``xtol`` is the tolerance of `BracketingSolver`'s rule; the corresponding parameter
      of the ALGOL procedure is ``delta``.

Validation:
    - A - authors' results:
      - used: Table 1, the errors of ``x_2`` to ``x_9``, reproduced to the printed digits, which is convincing (P5);
      - not used: Table 1's ``x_10``, and Tables 2 to 7; the docstring of the test package
        ``tests.solvers.bracketing.illinois`` gives the reasons.
    - B - third-party results:
      - used: Ford (1997), Table 4, reproduced to within 1 iteration, which is convincing (P5);
      - not used: the Illinois columns of other articles; the docstring of the test package
        ``tests.solvers.bracketing.illinois`` lists them, with the reasons.
      - TBD: Oliveira and Takahashi (2020), Table 1, the column "Illinois": 17 of its 24 counts match exactly and 23
        within 1, and the choice of form in the PRINCIPLE-GAP (P6) entry changes these counts.
    - C - reference implementation:
      - used: a twin test checks that `Illinois` evaluates the same x-values as mpmath's ``Illinois`` with
        ``method="illinois"``; the twin test imposes the stopping rule of `Illinois` on mpmath.

Variants:
    - `IllinoisConfig`, the only config, is core (P8).
"""

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

    `Illinois` stops by `BracketingSolver`'s criterion, so the returned x-value lies within ``xtol`` of a root.

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
