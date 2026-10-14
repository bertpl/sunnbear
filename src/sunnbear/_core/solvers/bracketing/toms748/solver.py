"""`TOMS748` implements Algorithm 748: interpolation steps, a double-size secant step, and bisection if needed.

The rest of this docstring is the record of `TOMS748` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

The names ``a``, ``b``, ``u``, ``k``, ``macheps``, ``tol`` and ``stop_width`` are those of the class docstring of
`TOMS748`.

Sources:
    - I - article:
      - Ia - article code: none: the authors' Fortran code is published with the article, not printed in it;
      - Ib - article pseudocode: Alefeld, Potra and Shi (1995):
        - Algorithms 4.1 and 4.2 in its section 4;
        - the subroutines ``bracket`` and Newton-Quadratic in its section 2, and ``ipzero`` in its section 3;
        - the modified ``bracket`` in its section 6, which adds the margin from the interval bounds and the stopping
          test;
      - Ic - article text: Alefeld, Potra and Shi (1995), its sections 2 and 6:
        - the assumption ``f(a) * f(b) < 0``;
        - the stopping criterion (equation 25);
        - ``mu = 0.5`` and ``lambda = 0.7``;
        - the relative machine precision of the article's runs.
    - II - authors' code:
      - the Fortran 77 code of Algorithm 748, which implements Algorithm 4.2 only, with a test driver that prints the
        root of each of its 154 test problems.
    - III - third party:
      - SciPy's ``scipy.optimize.toms748``: Algorithms 4.1 and 4.2 and higher values of ``k``, with ``k = 1`` as its
        default.
    - IV - own judgment:
      - the translation of ``xtol`` into the code's ``tol`` (P7).

Source per aspect:
    Every aspect follows Algorithms 4.1 and 4.2 of Alefeld, Potra and Shi (1995), with the modified ``bracket`` of
    their section 6, which their runs used, except:
    - Where the article leaves a detail open, the code follows the authors' Fortran code:
      - where a Newton step would divide by a zero derivative of the quadratic, Newton-Quadratic returns the zero of
        the line through ``a`` and ``b``, as the article's Newton-Quadratic does where the quadratic's leading
        coefficient is 0;
      - ``macheps`` is 2^-52, the relative machine precision of float64 as the authors' code's subroutine ``RMP``
        computes it; the article gives only the relative machine precision of its own machine, 1.9073486328e-16; with
        that value, ``k = 2`` misses 1 more count of Table VI than with 2^-52: the count of problem 3 with ``n = 1``,
        written 3[n=1] below;
      - the stopping test also runs before the first step;
      - ``u`` is ``b`` where ``|f(a)| = |f(b)|``;
      - the solve returns the lower bound ``a``.
    - PRINCIPLE-CONFLICT (P6): the code computes every formula in the form of the authors' Fortran code, where the
      article's pseudocode writes 4 of them in other forms:
      - the secant step, which the article computes with the divided difference ``f[a, b] = (f(b) - f(a)) / (b - a)``;
      - the double-size secant step, which the article computes with ``f[a, b]`` too;
      - Newton-Quadratic's quadratic and its derivative;
      - the midpoint ``0.5 * (a + b)``.
      P1 ranks the article above the authors' code, and for ``k = 2`` the article's results give no reason under P2
      for the authors' forms: those results do not reproduce better with them. With the article's forms:
      - ``k = 2`` still matches 15 of the 17 counts of Tables IV to VI, its Table II totals at ``tol = 10^-15`` and at
        ``tol = 0`` come 3 and 6 evaluations closer to the article's, and it misses the root that the authors' code
        prints for 26[n=1];
      - ``k = 1`` misses 1 more count of Table VI than with the authors' forms: 18 evaluations against the article's
        17 on 24[n=20].
      Either of 2 changes would resolve the conflict: computing these 4 formulas in the article's forms, or a principle
      that ranks as Ia the code that a journal publishes with its article; ACM publishes the code of Algorithm 748 that
      way.
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound, as for every
      solver. The article assumes ``f(a) * f(b) < 0``. Where f is 0 at such a bound, the authors' code:
      - at the lower bound, replaces that bound by the first new x-value, and ends near the upper bound, away from the
        root;
      - at the upper bound, returns an x-value within ``stop_width`` of that bound, after 1 more evaluation.
    - Translation of ``xtol`` (P7): ``tol = xtol / 2 - 2 * macheps * max(|a0|, |b0|)``, with ``a0`` and ``b0`` the
      initial interval bounds, so that ``stop_width = 2 * (2 * macheps * |u| + tol)`` stays at most ``xtol``. Where
      ``xtol`` is below ``4 * macheps * max(|a0|, |b0|)``:
      - that ``tol`` would be negative, so ``tol`` is 0, the smallest value that the article admits;
      - the returned ``a`` lies within ``stop_width`` of a root, and ``stop_width`` can then exceed ``xtol``.
      The benchmark keeps ``xtol`` above ``4 * macheps * max(|a0|, |b0|)``.

Validation:
    - A - authors' results:
      - used: Tables IV to VI, the evaluation counts of 17 problems at ``tol = 10^-15``. ``k = 2`` matches 15 of the 17
        counts exactly and the count of 28[n=30] within 1, which is convincing (P5); ``k = 1`` matches 13 exactly, and
        on macOS also the count of 18[n=1]. 26[n=1] is not compared, because its results depend on how its function is
        coded, as the article's section 6 states.
      - used: Table II, the total evaluation counts over the 154 problems at 4 values of ``tol``: within 0.4 % for
        ``k = 2``, which is convincing (P5), and 1.1 % for ``k = 1``. In float64, problem 26's function
        ``x / exp(1 / x^2)`` is 0 for ``|x|`` below about 0.0375, where ``exp`` overflows; with problem 26's function
        coded so that `TOMS748` reaches the problem's root 0, as section 6 reports for the article's runs, 7 of the 8
        totals lie within 0.15 %, and ``k = 1`` at ``tol = 0`` within 0.71 %.
      - PRINCIPLE-CONFLICT (P5): for ``k = 1``, the test data explains 2 deviations by the authors' own implementation
        of Algorithm 4.1, which may differ in details that the article does not state:
        - 3[n=1]: 13 evaluations against 15;
        - 13[n=1]: 26 against 25.
        P5 asks that the tests mark a small deviation of unverified cause with ``UNSTATED_RUN_DETAILS`` and a short
        observation instead. Marking 13[n=1] with ``UNSTATED_RUN_DETAILS`` and an observation, and giving 3[n=1] the
        reason that its count depends on the last bits of f, would resolve the conflict: a change of f by up to 2 ulps
        moves that count between 12 and 15.
      - not used: Table III, whose 139 problems the article does not list.
      - PRINCIPLE-GAP (P4): kind A covers results in the authors' article, and no kind covers the roots that the
        authors' test driver prints, which are published with the authors' code. The test suite checks them as
        authors' results: ``k = 2`` returns all 154 roots at ``tol = 0``. The roots tell ``k = 2`` from ``k = 1`` only
        on 26[n=1].
    - B - third-party results:
      - none found: Gao (2026), Table 3, prints the totals of Algorithm 4.2 from Table II, and reports no run of its
        own.
    - C - reference implementation:
      - not used: SciPy's ``scipy.optimize.toms748``, which keeps no margin from the interval bounds, computes its
        steps in other forms, and has its own fallbacks and stopping rule;
      - TBD: a twin test against the authors' Fortran code, which the tests would have to compile.

Variants:
    - `TOMS748K2Config`, with ``k = 2``, the article's Algorithm 4.2, is core (P8).
    - `TOMS748K1Config`, with ``k = 1``, Algorithm 4.1, is secondary (P8); the PRINCIPLE-CONFLICT (P5) above concerns
      its test data, and:
      - PRINCIPLE-GAP (P8): P8 admits a variant whose implementation decision causes fundamentally different behavior,
        and does not say how large that difference must be. For this config:
        - the article gives Algorithm 4.1 an asymptotic efficiency index of 1.6529 against 1.6686 for Algorithm 4.2,
          and 1.7 to 2.3 % more evaluations than Algorithm 4.2 in Table II;
        - the code keeps the config; the config's docstring gives as the reason that ``k = 1`` is SciPy's default.
"""

from sunnbear._core.solvers.core import Interval, IntervalBound, Solver, SolveState
from sunnbear._core.utils.floats import FLOAT64_EPS

# ``_MU`` is the paper's ``mu``: an iteration that leaves the interval at least ``_MU`` times as wide as at the start of
# the iteration ends with a bisection.
_MU = 0.5

# ``_LAMBDA`` is the paper's ``lambda``: `_evaluate_and_split_at` uses it to keep each new x-value away from the bounds
# of the interval.
_LAMBDA = 0.7

# The authors' code starts ``e`` and ``f(e)`` at this value, which no step reads. ``e`` is the bound discarded before
# the most recently discarded one; the only step that runs before ``e`` is set, the first interpolation step of the
# second iteration, always takes Newton steps, which do not read ``e``.
_UNSET = 1.0e5


class TOMS748(Solver):
    """`TOMS748` implements Algorithm 748 (Alefeld, Potra and Shi, 1995), with ``k`` interpolation steps per iteration.

    The first iteration takes a secant step. Each later iteration evaluates the function at 1 x-value per step:

    - ``k`` interpolation steps. The j-th step, counted from 1, takes the zero of the inverse cubic interpolation
      through the bounds ``a`` and ``b`` and the 2 most recently discarded bounds, ``d`` and ``e``. When the 4
      function values are not distinct, or when that zero lies outside ``(a, b)``, it takes ``j + 1`` Newton steps
      on the quadratic through ``a``, ``b`` and ``d``. The first step of the second iteration always takes the
      Newton steps, because ``e`` is not known yet.
    - a double-size secant step: from ``u``, the bound with the smaller ``|f|``, a step twice as long as the secant
      step; when that step would be longer than half the interval, the midpoint instead.
    - a bisection, unless the interval has shrunk below half its width at the start of the iteration.

    ``k = 1`` is the paper's Algorithm 4.1 and ``k = 2`` its Algorithm 4.2.

    The paper states the 2 algorithms without a stopping criterion; its experiments, and the authors' code, add the
    stopping criterion of Brent's method:

    - ``stop_width = 2 * (2 * macheps * |u| + tol)``, with ``macheps`` the relative machine precision
      (`FLOAT64_EPS`) and ``tol`` an absolute tolerance that the solver derives from ``xtol``;
    - the solve ends once the interval is at most ``stop_width`` wide, or once an evaluation returns exactly 0, and
      returns the lower bound ``a``, or the x-value that returned 0.

    The experiments and the code also keep every new x-value at least ``0.7 * stop_width`` inside the interval, and
    take the midpoint when the interval is at most ``1.4 * stop_width`` wide.

    The returned ``a`` lies within ``stop_width`` of a root. The solver sets
    ``tol = xtol / 2 - 2 * macheps * max(|a0|, |b0|)``, with ``a0`` and ``b0`` the bounds of the initial interval, so
    that ``stop_width`` never exceeds ``xtol``.

    Where ``xtol`` is below ``4 * macheps * max(|a0|, |b0|)``, ``tol`` would be negative and the margin of 0.7 times
    ``stop_width`` could move an x-value outside the interval; the solver then sets ``tol = 0``, the setting of the
    authors' test runs, and the accuracy of ``xtol`` is no longer guaranteed.

    An iteration of `TOMS748` evaluates the function up to ``k + 2`` times, so `TOMS748` writes its own loop, not
    `BracketingSolver`'s.

    References:
        - Alefeld, G. E., Potra, F. A. and Shi, Y. (1995). Algorithm 748: Enclosing zeros of continuous functions.
          ACM Transactions on Mathematical Software 21(3), 327-344. Its subroutine ``ipzero`` is the inverse cubic
          interpolation, and its section 6 states the stopping criterion and the margin. The test suite compares the
          evaluation counts of `TOMS748` with the paper's Tables II and IV to VI. https://doi.org/10.1145/210089.210111
        - The authors' Fortran 77 code, published with the paper as algorithm 748 of the Collected Algorithms of the
          ACM, https://www.netlib.org/toms/748. It implements Algorithm 4.2, which ``k = 2`` follows line by line, and
          the test suite reproduces the roots that the code's test driver prints for its test problems.
        - SciPy's ``scipy.optimize.toms748``, which implements Algorithms 4.1 and 4.2, with ``k = 1`` as its default.
          It keeps no margin from the interval bounds. Once per iteration, it tests whether the interval is at most
          ``xtol + rtol * |b|`` wide, and if so, it stops and returns the interval's midpoint.
        - Gao, F. (2026). Fast and stable root-finding using clipped power interpolations. Applied Mathematics Letters
          178, 109928. Its Table 3 prints the totals of Algorithm 4.2 from the paper's Table II.
          https://doi.org/10.1016/j.aml.2026.109928
    """

    name = "toms748"
    version = 1

    def __init__(self, *, k: int) -> None:
        """Configure the number ``k`` of interpolation steps per iteration.

        ``k = 1`` and ``k = 2`` are the paper's Algorithms 4.1 and 4.2.

        Raises:
            ValueError: If ``k`` is not 1 or 2.
        """
        if k not in (1, 2):
            raise ValueError(f"k must be 1 or 2 (got {k}).")
        self.k = k

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with the authors' code
        """Run Algorithm 4.1 or 4.2 and return the lower bound of the final interval.

        The variables keep the names of the paper and the authors' code, so that this method can be compared with the
        paper and the authors' code step by step:

        - ``interval`` is the enclosing interval ``[a, b]``, with ``f(a)`` and ``f(b)`` of opposite signs;
        - ``d`` is the bound that the last call of `_evaluate_and_split_at` discarded, and ``e`` the value of ``d``
          before that call; both lie outside the interval, and ``fd`` and ``fe`` are their function values;
        - ``c`` is the x-value to evaluate next.

        Each call of `_evaluate_and_split_at` evaluates 1 x-value and returns the new interval; the solve ends after any
        call that returns an interval with ``f(a) = 0``, or one at most ``stop_width`` wide. A midpoint is computed as
        ``a + 0.5 * (b - a)``, as in the authors' code, not with `Interval.midpoint`, which rounds differently.
        """
        interval = state.interval
        tol = self._get_tol(state.xtol, interval.a, interval.b)
        # The first call of _evaluate_and_split_at sets d and fd before any step reads them.
        d = fd = e = fe = _UNSET
        n_iterations = 0
        while True:
            iteration_start_width = interval.width
            n_iterations += 1
            stop_width = self._get_stop_width(interval, tol)
            if interval.width <= stop_width:
                return interval.a

            # --- iteration 1: the secant step ---
            if n_iterations == 1:
                c = interval.a - (interval.fa / (interval.fb - interval.fa)) * interval.width
                interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
                if interval.is_fa_zero or interval.width <= stop_width:
                    return interval.a
                continue

            # --- the k interpolation steps ------
            for j in range(1, self.k + 1):
                a, b, fa, fb = interval.a, interval.b, interval.fa, interval.fb
                # The product is 0 exactly when 2 of the 4 function values are equal.
                product_of_f_differences = (fa - fb) * (fa - fd) * (fa - fe) * (fb - fd) * (fb - fe) * (fd - fe)
                if (j == 1 and n_iterations == 2) or product_of_f_differences == 0.0:
                    c = self._newton_quadratic_zero(a, b, d, fa, fb, fd, j + 1)
                else:
                    c = self._inverse_cubic_zero(a, b, d, e, fa, fb, fd, fe)
                    if (c - a) * (c - b) >= 0.0:
                        c = self._newton_quadratic_zero(a, b, d, fa, fb, fd, j + 1)
                if j < self.k:
                    # The next interpolation step uses this step's d as its e.
                    e, fe = d, fd
                interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
                if interval.is_fa_zero or interval.width <= stop_width:
                    return interval.a
            e, fe = d, fd

            # --- the double-size secant step ----
            u, fu = self._get_u(interval)
            c = u - 2.0 * (fu / (interval.fb - interval.fa)) * interval.width
            if abs(c - u) > 0.5 * interval.width:
                c = interval.a + 0.5 * interval.width
            interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
            if interval.is_fa_zero or interval.width <= stop_width:
                return interval.a

            # --- the bisection, if needed -------
            if interval.width < _MU * iteration_start_width:
                continue
            e, fe = d, fd
            c = interval.a + 0.5 * interval.width
            interval, d, fd, stop_width = self._evaluate_and_split_at(state, interval, c, stop_width, tol)
            if interval.is_fa_zero or interval.width <= stop_width:
                return interval.a

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _get_tol(xtol: float, a0: float, b0: float) -> float:
        """Return the ``tol`` that keeps ``stop_width`` at most ``xtol``, or 0 where that ``tol`` would be negative.

        The test suite overrides this method to apply the paper's tolerance when it reproduces the paper's tables.
        """
        return max(0.5 * xtol - 2.0 * FLOAT64_EPS * max(abs(a0), abs(b0)), 0.0)

    @staticmethod
    def _get_u(interval: Interval) -> tuple[float, float]:
        """Return ``u``, the bound with the smaller ``|f|``, and ``b`` when both are equal, with ``f(u)``."""
        if abs(interval.fb) <= abs(interval.fa):
            return interval.b, interval.fb
        else:
            return interval.a, interval.fa

    @staticmethod
    def _get_stop_width(interval: Interval, tol: float) -> float:
        """Return ``stop_width = 2 * (2 * macheps * |u| + tol)`` for ``interval``, the authors' subroutine ``TOLE``."""
        u, _ = TOMS748._get_u(interval)
        return 2.0 * (tol + 2.0 * abs(u) * FLOAT64_EPS)

    def _evaluate_and_split_at(
        self, state: SolveState, interval: Interval, c: float, stop_width: float, tol: float
    ) -> tuple[Interval, float, float, float]:
        """Evaluate ``c`` and return the interval that still holds the sign change: the authors' subroutine ``BRACKT``.

        Before the evaluation, ``c`` is moved to at least ``_LAMBDA * stop_width`` inside the interval, or to the
        midpoint when the interval is at most ``2 * _LAMBDA * stop_width`` wide. The method also sets
        ``state.x_best`` to the lower bound of the new interval.

        Returns:
            A tuple of:

            - the new interval; if ``f(c)`` is exactly 0, it is ``[c, b]`` with ``f(a) = 0``;
            - the discarded bound ``d``;
            - ``f(d)``;
            - the ``stop_width`` of the new interval.
        """
        margin = _LAMBDA * stop_width
        if interval.width <= 2.0 * margin:
            c = interval.a + 0.5 * interval.width
        elif c <= interval.a + margin:
            c = interval.a + margin
        elif c >= interval.b - margin:
            c = interval.b - margin
        fc = state.f(c)
        # split_at treats a zero f(c) as having the sign of f(a), so it replaces a with c.
        new_interval = interval.split_at(c, fc)
        if new_interval.last_replaced_bound is IntervalBound.LOWER:
            d, fd = interval.a, interval.fa
        else:
            d, fd = interval.b, interval.fb
        state.x_best = new_interval.a
        return new_interval, d, fd, self._get_stop_width(new_interval, tol)

    @staticmethod
    def _newton_quadratic_zero(a: float, b: float, d: float, fa: float, fb: float, fd: float, n_steps: int) -> float:
        """Return the zero in ``(a, b)`` of the quadratic through ``a``, ``b`` and ``d``, by ``n_steps`` Newton steps.

        This is the paper's subroutine Newton-Quadratic, as the authors' subroutine ``NEWQUA`` implements it.

        The quadratic is ``p(x) = fa + a1 * (x - a) + a2 * (x - a) * (x - b)``, with the divided differences
        ``a1 = f[a, b]`` and ``a2 = f[a, b, d]``. The Newton steps start from the bound where ``p`` has the same sign
        as ``p'' = 2 * a2``; from that bound, each step moves toward the zero without passing it.

        When ``a2 = 0``, or when a step meets ``p'(x) = 0``, the zero of the line ``fa + a1 * (x - a)`` is returned.
        """
        a1 = (fb - fa) / (b - a)
        a2 = ((fd - fb) / (d - b) - a1) / (d - a)
        if a2 == 0.0:
            return a - fa / a1
        else:
            if (a2 > 0.0) == (fa > 0.0):
                c = a
            else:
                c = b
            for _ in range(n_steps):
                pc = fa + (a1 + a2 * (c - b)) * (c - a)
                pdc = a1 + a2 * ((2.0 * c) - (a + b))
                if pdc == 0.0:
                    return a - fa / a1
                c = c - pc / pdc
            return c

    @staticmethod
    def _inverse_cubic_zero(
        a: float, b: float, d: float, e: float, fa: float, fb: float, fd: float, fe: float
    ) -> float:
        """Return the zero of the inverse cubic interpolation through ``a``, ``b``, ``d`` and ``e``.

        This is the paper's subroutine ``ipzero``, the authors' subroutine ``PZERO``: an Aitken-Neville scheme for the
        value at ``y = 0`` of the cubic ``x(y)`` through the 4 points ``(f(x), x)``. The 4 function values must be
        distinct.
        """
        q11 = (d - e) * fd / (fe - fd)
        q21 = (b - d) * fb / (fd - fb)
        q31 = (a - b) * fa / (fb - fa)
        d21 = (b - d) * fd / (fd - fb)
        d31 = (a - b) * fb / (fb - fa)
        q22 = (d21 - q11) * fb / (fe - fb)
        q32 = (d31 - q21) * fa / (fd - fa)
        d32 = (d31 - q21) * fd / (fd - fa)
        q33 = (d32 - q22) * fa / (fe - fa)
        return a + (q31 + q32 + q33)
