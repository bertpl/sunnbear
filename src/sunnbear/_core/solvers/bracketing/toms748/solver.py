"""`TOMS748` implements Algorithm 748: interpolation steps, a double-size secant step, and bisection if needed."""

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

    As in the paper's experiments and the authors' code, every step keeps its new x-value at least ``0.7*(2*tole)``
    inside the interval, with the paper's tolerance ``tole``, defined below, and takes the midpoint instead when the
    interval is at most twice that margin wide:

    - ``tole = 2*macheps*|u| + tol`` is the paper's tolerance, with ``macheps`` the relative machine precision,
      `FLOAT64_EPS`;
    - ``tol`` is ``xtol``; the paper leaves this absolute tolerance to its caller. The margin is then about
      ``0.7*(2*xtol)``, the same fraction of the shared stopping width ``2*xtol`` as the paper's margin is of its
      stopping width ``2*tole``.

    For an ``xtol`` below the float spacing near the root, the interval never shrinks to ``2*xtol``, and the solve ends
    as a solver error.

    Once the interval is 1 float spacing wide, its midpoint rounds onto a bound, which then also becomes ``d``, and the
    next Newton-Quadratic step divides by ``d - a = 0``.

    An iteration of `TOMS748` evaluates the function up to ``k + 2`` times, so `TOMS748` writes its own loop, not
    `BracketingSolver`'s.

    `TOMS748` departs from the paper or the authors' code in these places:

    - **Stopping criterion:** `TOMS748` checks the shared stopping criterion where the authors' code checks its own,
      before each iteration and after each evaluation:

      - the solve ends once the interval is at most ``2*xtol`` wide, or once the function value at an interval bound
        is exactly 0, and returns that bound, or else the interval's midpoint, which then lies within ``xtol`` of a
        root;
      - the paper's experiments and the authors' code end the solve once the interval is at most ``2*tole`` wide, or
        once an evaluation returns exactly 0, and the code returns the lower bound ``a``.
    - **Chord's zero and midpoint:** the first secant step and every midpoint take the shared forms of `chord_zero`
      and `midpoint`; the authors' code computes them as ``a - (fa/(fb - fa))*(b - a)`` and ``a + 0.5*(b - a)``.
    - **Forms of the authors' code:** 2 formulas take the forms of the authors' code, which round differently from
      the forms of the paper:

      - the double-size secant step, ``u - 2*(fu/(fb - fa))*(b - a)``, which the paper writes as
        ``u - 2*f(u)/f[a, b]``, with ``f[a, b] = (fb - fa)/(b - a)``;
      - Newton-Quadratic's quadratic, ``fa + (a1 + a2*(x - b))*(x - a)``, which the paper writes as
        ``fa + a1*(x - a) + a2*(x - a)*(x - b)``, with the divided differences ``a1 = f[a, b]`` and
        ``a2 = f[a, b, d]``.

    References:
        - Alefeld, G. E., Potra, F. A. and Shi, Y. (1995). Algorithm 748: Enclosing zeros of continuous functions.
          ACM Transactions on Mathematical Software 21(3), 327-344. It states Algorithms 4.1 and 4.2 and the inverse
          cubic interpolation ``ipzero``; its section 6 states the margin, and the stopping criterion with which the
          test suite reproduces its Tables II and IV to VI. https://doi.org/10.1145/210089.210111
        - The authors' Fortran 77 code, published with the paper as algorithm 748 of the Collected Algorithms of the
          ACM, https://www.netlib.org/toms/748. It implements only Algorithm 4.2, which ``k = 2`` follows line by line
          apart from the deviations above, and the test suite reproduces the roots that its test driver prints for its
          test problems.
    """

    name = "toms748"
    version = 3

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
        """Run Algorithm 4.1 or 4.2 until `_root_if_converged` returns a root estimate, and return that estimate.

        The variables keep the names of the paper and the authors' code, so that this method can be compared with the
        paper and the authors' code step by step:

        - ``interval`` is the enclosing interval ``[a, b]``, with ``f(a)`` and ``f(b)`` of opposite signs;
        - ``d`` is the bound that the last call of `_evaluate_and_split_at` discarded, and ``e`` the value of ``d``
          before that call; both lie outside the interval, and ``fd`` and ``fe`` are their function values;
        - ``c`` is the x-value to evaluate next;
        - ``tol`` is the paper's absolute tolerance, and ``tole_doubled`` is ``2*tole``, which the authors' code keeps
          in its variable ``TOL``.

        The method calls `_root_if_converged` where the authors' code checks its stopping criterion: at the top of each
        iteration, the authors' label 10, and after each call of `_evaluate_and_split_at`, which evaluates 1 x-value.
        """
        interval = state.interval
        tol = state.xtol
        xtol_doubled = 2.0 * state.xtol
        # The first call of _evaluate_and_split_at sets d and fd before any step reads them.
        d = fd = e = fe = _UNSET
        n_iterations = 0
        while True:
            iteration_start_width = interval.width
            n_iterations += 1
            tole_doubled = self._get_tole_doubled(interval, tol)
            x_root = self._root_if_converged(interval, xtol_doubled, tole_doubled)
            if x_root is not None:
                return x_root

            # --- iteration 1: the secant step ---
            if n_iterations == 1:
                c = interval.chord_zero
                interval, d, fd, tole_doubled = self._evaluate_and_split_at(state, interval, c, tole_doubled, tol)
                x_root = self._root_if_converged(interval, xtol_doubled, tole_doubled)
                if x_root is not None:
                    return x_root
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
                interval, d, fd, tole_doubled = self._evaluate_and_split_at(state, interval, c, tole_doubled, tol)
                x_root = self._root_if_converged(interval, xtol_doubled, tole_doubled)
                if x_root is not None:
                    return x_root
            e, fe = d, fd

            # --- the double-size secant step ----
            u, fu = self._get_u(interval)
            c = u - 2.0 * (fu / (interval.fb - interval.fa)) * interval.width
            if abs(c - u) > 0.5 * interval.width:
                c = interval.midpoint
            interval, d, fd, tole_doubled = self._evaluate_and_split_at(state, interval, c, tole_doubled, tol)
            x_root = self._root_if_converged(interval, xtol_doubled, tole_doubled)
            if x_root is not None:
                return x_root

            # --- the bisection, if needed -------
            if interval.width < _MU * iteration_start_width:
                continue
            e, fe = d, fd
            c = interval.midpoint
            interval, d, fd, tole_doubled = self._evaluate_and_split_at(state, interval, c, tole_doubled, tol)
            x_root = self._root_if_converged(interval, xtol_doubled, tole_doubled)
            if x_root is not None:
                return x_root

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _root_if_converged(interval: Interval, xtol_doubled: float, tole_doubled: float) -> float | None:
        """Return the root estimate if the shared stopping criterion holds for ``interval``, else ``None``.

        ``tole_doubled`` is unused here. The test suite overrides this method with the stopping criterion of the
        authors' code, which reads ``tole_doubled``, to reproduce the paper's tables and the roots that the authors'
        code prints.
        """
        if interval.is_converged(xtol_doubled):
            return interval.root()
        else:
            return None

    @staticmethod
    def _get_u(interval: Interval) -> tuple[float, float]:
        """Return ``u``, the bound with the smaller ``|f|``, and ``b`` when both are equal, with ``f(u)``."""
        if abs(interval.fb) <= abs(interval.fa):
            return interval.b, interval.fb
        else:
            return interval.a, interval.fa

    @staticmethod
    def _get_tole_doubled(interval: Interval, tol: float) -> float:
        """Return ``2*tole`` for ``interval``, with ``tole = 2*macheps*|u| + tol``.

        The authors' subroutine ``TOLE`` computes this value and returns it in its argument ``TOL``.
        """
        u, _ = TOMS748._get_u(interval)
        return 2.0 * (tol + 2.0 * abs(u) * FLOAT64_EPS)

    def _evaluate_and_split_at(
        self, state: SolveState, interval: Interval, c: float, tole_doubled: float, tol: float
    ) -> tuple[Interval, float, float, float]:
        """Evaluate ``c`` and return the interval that still holds the sign change: the authors' subroutine ``BRACKT``.

        Before the evaluation, ``c`` is moved to at least ``_LAMBDA*tole_doubled`` inside the interval, or to the
        midpoint when the interval is at most ``2*_LAMBDA*tole_doubled`` wide. After the evaluation, the method sets
        ``state.x_best`` to ``c``, the latest evaluated x-value.

        Returns:
            A tuple of:

            - the new interval; if ``f(c)`` is exactly 0, it is ``[c, b]`` with ``f(a) = 0``;
            - the discarded bound ``d``;
            - ``f(d)``;
            - ``2*tole`` for the new interval.
        """
        margin = _LAMBDA * tole_doubled
        if interval.width <= 2.0 * margin:
            c = interval.midpoint
        elif c <= interval.a + margin:
            c = interval.a + margin
        elif c >= interval.b - margin:
            c = interval.b - margin
        fc = state.f(c)
        state.x_best = c
        # split_at treats a zero f(c) as having the sign of f(a), so it replaces a with c.
        new_interval = interval.split_at(c, fc)
        if new_interval.last_replaced_bound is IntervalBound.LOWER:
            d, fd = interval.a, interval.fa
        else:
            d, fd = interval.b, interval.fb
        return new_interval, d, fd, self._get_tole_doubled(new_interval, tol)

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
