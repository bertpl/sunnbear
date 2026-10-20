"""`TOMS748` implements Algorithms 4.1 and 4.2 of Alefeld, Potra and Shi (1995), as the paper states them."""

import math

from sunnbear._core.solvers.core import Solver, SolveState
from sunnbear._core.solvers.core.stopping import interval_root_if_converged
from sunnbear._core.utils.floats import FLOAT64_EPS


class TOMS748(Solver):
    """`TOMS748` implements Algorithms 4.1 and 4.2 of Alefeld, Potra and Shi (1995), as the paper states them.

    ``k`` selects the algorithm: ``k = 1`` is Algorithm 4.1, and ``k = 2`` is Algorithm 4.2. The paper's section 5
    names this ``k`` in its Algorithm 5.7, of which Algorithms 4.1 and 4.2 are the cases ``k = 1`` and ``k = 2``.

    Each iteration ``n``, counted from ``n = 2``, starts from the interval ``[a_n, b_n]``, where ``f`` changes sign,
    and from up to 2 earlier x-values outside it.

    The subroutine ``bracket`` keeps the part of the interval that holds the sign change and drops the other bound:
    ``d_n`` is the bound that the last call of ``bracket`` dropped, and ``e_n`` the bound that the second-to-last call
    dropped.

    The iteration takes these steps, numbered as in Algorithm 4.1:

    - **4.1.3, an interpolation step:** the zero of the inverse cubic interpolation through ``a_n``, ``b_n``, ``d_n``
      and ``e_n``, from the subroutine ``ipzero``. In 3 cases, the step takes 2 Newton steps on the quadratic
      interpolation through ``a_n``, ``b_n`` and ``d_n`` instead, from the subroutine ``Newton-Quadratic``: at
      ``n = 2``, where 2 of the 4 function values are equal, and where the zero of ``ipzero`` lies outside
      ``(a_n, b_n)``;
    - **4.1.5 to 4.1.7, a double-length secant step:** on the interval ``[a_bar, b_bar]`` after the interpolation
      step, ``c_bar = u - 2*f(u) / f[a_bar, b_bar]``, from the bound ``u`` of that interval with the smaller ``|f|``,
      with ``f[a, b] = (f(b) - f(a)) / (b - a)``. Where ``c_bar`` lies more than half the width of ``[a_bar, b_bar]``
      from ``u``, the midpoint of ``[a_bar, b_bar]`` replaces ``c_bar``;
    - **4.1.9, a bisection:** only where the 2 steps above have not reduced the interval to less than ``mu = 0.5``
      times the width of ``[a_n, b_n]``.

    Algorithm 4.2 repeats the interpolation step once, in its steps 4.2.5 and 4.2.6, on the interval after the first
    interpolation step; where the repeated step falls back to ``Newton-Quadratic``, it takes 3 Newton steps in place
    of 2. Before the first iteration, which is ``n = 2``, step 4.1.1 takes a secant step from ``a_1``.

    Each step passes its x-value ``c`` to ``bracket``, which evaluates ``f`` there. `TOMS748` implements
    ``bracket`` as the paper's section 6 modifies it for the paper's experiments, with a margin and a termination test:

    - **the margin:** ``bracket`` first sets ``delta = lambda*tole(a, b)``, with ``lambda = 0.7``. Here
      ``tole(a, b) = 2*|u|*macheps + tol``, where ``tol`` is the paper's absolute tolerance, ``macheps`` its relative
      machine precision, and ``u`` the bound with the smaller ``|f|``. Where the interval is at most ``4*delta`` wide,
      ``c`` becomes the midpoint; elsewhere, a ``c`` that lies less than ``2*delta`` inside the interval, or outside
      it, moves to ``2*delta`` from the nearer bound;
    - **the termination test:** ``bracket`` ends the solve once ``f(c) = 0``, or once the new interval
      ``[a_bar, b_bar]`` is at most ``2*tole(a_bar, b_bar)`` wide.

    In place of that test, the shared stopping criterion of the bracketing solvers ends the solve once the new interval
    is at most ``2*xtol`` wide, or once ``f`` is exactly 0 at one of its bounds; that bound is then ``c``. `TOMS748`
    returns that bound, or else the interval's midpoint, which then lies within ``xtol`` of a root.

    Each iteration calls ``bracket`` 2 or 3 times with ``k = 1``, and 3 or 4 times with ``k = 2``.

    The paper's tolerances take these values in `TOMS748`:

    - ``tol``, the paper's absolute tolerance, is ``xtol``:

      - the paper's termination test then holds once the interval is at most ``2*xtol + 4*|u|*macheps`` wide; the
        shared stopping criterion drops the term ``4*|u|*macheps`` and holds at ``2*xtol``;
      - the margin ``2*delta`` is then about ``1.4*xtol``, which is ``lambda`` times ``2*xtol``, as the paper's margin
        is ``lambda`` times the width ``2*tole`` of its termination test;
      - where a step lands ``2*delta`` from the bound next to the root, with the root between them, the new interval
        is ``2*delta`` wide, narrower than ``2*xtol``, so the solve ends; and because the margin is larger than 0, no
        step lands on a bound;
    - ``macheps``, the paper's relative machine precision, is `FLOAT64_EPS`, 2^-52, the distance from 1.0 to the next
      larger float64. The paper states the machine precision of its own computer, 1.9073486328e-16, but takes its
      termination test from Brent's method; `TOMS748` therefore takes ``macheps`` as 2^-52, the value that the
      `Brent` solver takes. ``macheps`` enters only the margin of ``bracket``, not the stopping criterion.

    `TOMS748` departs from the paper in these places:

    - **Stopping criterion and return value:** the shared stopping criterion above replaces the paper's termination
      test, at the same point: after each call of ``bracket``. The paper does not state which x-value its runs return
      when the interval has become narrow enough for its termination test.
    - **Tests written as products:** the paper states these tests as the sign of a product, or as a product equal
      to 0. `TOMS748` tests the factors instead, because a product of small numbers can underflow to 0, which
      changes the outcome of the test:

      - ``f(a)f(c) < 0`` and ``f(b)f(c) < 0`` in ``bracket``: the signs of ``f(a)`` and ``f(c)`` are compared, which
        also decides the second test, because ``f(a)`` and ``f(b)`` differ in sign;
      - ``A*f(a) > 0`` in ``Newton-Quadratic``: the signs of ``A`` and ``f(a)`` are compared;
      - ``(c_n - a_n)(c_n - b_n) >= 0`` in steps 4.1.3, 4.2.3 and 4.2.5: ``c_n`` is compared with ``a_n`` and
        ``b_n``;
      - ``prod_(i != j) (f_i - f_j) = 0`` in steps 4.1.3, 4.2.3 and 4.2.5, which holds where 2 of the 4 function
        values are equal: the values are compared pair by pair.

    `TOMS748` reads the paper's text in these places, where the text allows more than 1 reading:

    - **The Newton step, the paper's equation (4):** its second line divides ``B(r_(i-1))`` by the derivative of ``P``;
      ``B(r_(i-1))`` is a typo for ``P(r_(i-1))``, the numerator of its first line.
    - **The case** ``A = 0`` **of** ``Newton-Quadratic``: `TOMS748` reads the statement ``r = a - B^-1 f(a)`` as the
      end of the subroutine, because the Newton steps that the paper lists after it would replace that ``r``, and
      the statement would then have no effect.
    - **The inverse notation:** the paper writes a division by a divided difference as a product with its inverse, as
      in ``f[a, b]^-1 f(a)``; `TOMS748` computes it as 1 division, ``f(a) / f[a, b]``.
    - **The products in** ``ipzero``: each of its quantities ``Q11`` to ``Q33`` and ``D21`` to ``D32`` is a
      difference of x-values times a fraction of function values, such as ``Q11 = (c - d)*(f(c) / (f(d) - f(c)))``,
      computed with the fraction first, as the paper typesets it.

    `TOMS748` settles 1 case that the paper leaves open, a tie in ``tole``: where ``|f(a)| = |f(b)|``, ``u`` is
    ``b``, by the rule of step 4.1.5, which picks ``u`` from the same 2 bounds.

    The formulas keep the paper's form, and with it these failures in float64:

    - The divided difference ``f[a, b]`` underflows to 0 where ``|f(b) - f(a)|`` is tiny next to ``b - a``; a step that
      divides by it then raises a ``ZeroDivisionError``, which `Solver.solve` records as ``SOLVER_ERROR``.
    - Where ``xtol`` lies below half the float spacing near the root, the shared stopping criterion never holds.

      Once the interval is 1 float spacing wide, the midpoint that ``bracket`` takes rounds onto a bound, which
      ``bracket`` returns both as an interval bound and as ``d``. ``Newton-Quadratic`` then divides by ``d - a = 0``
      or ``d - b = 0``, and the solve ends as ``SOLVER_ERROR``.

      With the machine-precision term, the paper's termination test ends the solve before the division by 0; the
      benchmark never sets such an ``xtol``.

    `TOMS748` keeps x-values besides the interval bounds, so it writes its own loop, not `BracketingSolver`'s.

    References:
        - Alefeld, G. E., Potra, F. A. and Shi, Y. (1995). Algorithm 748: Enclosing zeros of continuous functions. ACM
          Transactions on Mathematical Software 21(3), 327-344. Its sections 2 to 4 and 6 state the method, which
          `TOMS748` follows step by step, and the test suite reproduces the totals of its Table II and the
          counts of its Tables IV to VI. https://doi.org/10.1145/210089.210111
        - The test output that the authors publish with their code, as algorithm 748 of the Collected Algorithms
          of the ACM: the roots of the paper's test problems, which the test suite reproduces.
          https://www.netlib.org/toms/748
    """

    name = "toms748"
    version = 3

    # The paper's constants are mu of Algorithms 4.1 and 4.2, and lambda and macheps of the subroutine bracket of
    # section 6. The class docstring states the reasons for the value of macheps.
    mu = 0.5
    lambda_ = 0.7
    macheps = FLOAT64_EPS

    def __init__(self, *, k: int) -> None:
        """Configure ``k``, which selects Algorithm 4.1 (``k = 1``) or Algorithm 4.2 (``k = 2``).

        Raises:
            ValueError: If ``k`` is neither 1 nor 2.
        """
        if k not in (1, 2):
            raise ValueError(f"k must be 1 or 2 (got k={k!r}).")
        self.k = k

    def _solve(self, state: SolveState) -> float:  # noqa: C901 — helpers would break the step-by-step match with the paper
        """Run Algorithm 4.1 or 4.2 until `_root_if_converged` returns a root estimate, and return that estimate.

        The variables keep the paper's names, without the iteration's subscript ``n``: ``a``, ``b``, ``d`` and ``e``
        are ``a_n``, ``b_n``, ``d_n`` and ``e_n``. The suffixes ``_bar`` and ``_hat`` stand for the paper's bar and
        hat accents, as ``a_bar`` for ``a_n`` with a bar. A name with the prefix ``f`` holds the function value at the
        x-value of the name, as ``fa`` holds ``f(a)``.

        Each iteration takes the steps of the class docstring, and calls `_root_if_converged` after each call of
        ``bracket``, where the paper's section 6 places its termination test.
        """
        interval = state.interval
        a, fa, b, fb = interval.a, interval.fa, interval.b, interval.fb
        xtol_doubled = 2.0 * state.xtol

        # --- 4.1.1 / 4.2.1 ----------------------
        # c_1 = a_1 - f[a_1, b_1]^-1 f(a_1), with the divided difference f[a, b] = (f(b) - f(a)) / (b - a).
        c = a - fa / ((fb - fa) / (b - a))

        # --- 4.1.2 / 4.2.2 ----------------------
        a, fa, b, fb, d, fd = self.bracket(state, a, fa, b, fb, c)
        x_root = self._root_if_converged(state, a, fa, b, fb, xtol_doubled)
        if x_root is not None:
            return x_root

        # e_2 is not defined: step 4.1.3 does not read it at n = 2.
        e, fe = math.nan, math.nan
        n = 2
        while True:
            # --- 4.1.3 / 4.2.3 ------------------
            if n == 2 or self._has_2_equal_values(fa, fb, fd, fe):
                c = self.newton_quadratic(a, fa, b, fb, d, fd, 2)
            else:
                c = self.ipzero(a, fa, b, fb, d, fd, e, fe)
                # The comparisons test the factors of the paper's product (c_n - a_n)(c_n - b_n) >= 0.
                if c <= a or c >= b:
                    c = self.newton_quadratic(a, fa, b, fb, d, fd, 2)

            # --- 4.1.4 / 4.2.4 ------------------
            # e_bar is read only by step 4.2.5.
            e_bar, fe_bar = d, fd
            a_bar, fa_bar, b_bar, fb_bar, d_bar, fd_bar = self.bracket(state, a, fa, b, fb, c)
            x_root = self._root_if_converged(state, a_bar, fa_bar, b_bar, fb_bar, xtol_doubled)
            if x_root is not None:
                return x_root

            if self.k == 2:
                # --- 4.2.5 ----------------------
                if self._has_2_equal_values(fa_bar, fb_bar, fd_bar, fe_bar):
                    c_bar = self.newton_quadratic(a_bar, fa_bar, b_bar, fb_bar, d_bar, fd_bar, 3)
                else:
                    c_bar = self.ipzero(a_bar, fa_bar, b_bar, fb_bar, d_bar, fd_bar, e_bar, fe_bar)
                    # The comparisons test the factors of the paper's product
                    # (c_bar_n - a_bar_n)(c_bar_n - b_bar_n) >= 0.
                    if c_bar <= a_bar or c_bar >= b_bar:
                        c_bar = self.newton_quadratic(a_bar, fa_bar, b_bar, fb_bar, d_bar, fd_bar, 3)

                # --- 4.2.6 ----------------------
                a_bar, fa_bar, b_bar, fb_bar, d_bar, fd_bar = self.bracket(state, a_bar, fa_bar, b_bar, fb_bar, c_bar)
                x_root = self._root_if_converged(state, a_bar, fa_bar, b_bar, fb_bar, xtol_doubled)
                if x_root is not None:
                    return x_root

            # --- 4.1.5 / 4.2.7 ------------------
            if abs(fa_bar) < abs(fb_bar):
                u, fu = a_bar, fa_bar
            else:
                u, fu = b_bar, fb_bar

            # --- 4.1.6 / 4.2.8 ------------------
            # c_bar_n = u_n - 2 f[a_bar_n, b_bar_n]^-1 f(u_n), the double-length secant step from u_n.
            c_bar = u - 2.0 * fu / ((fb_bar - fa_bar) / (b_bar - a_bar))

            # --- 4.1.7 / 4.2.9 ------------------
            if abs(c_bar - u) > 0.5 * (b_bar - a_bar):
                c_hat = 0.5 * (b_bar + a_bar)
            else:
                c_hat = c_bar

            # --- 4.1.8 / 4.2.10 -----------------
            a_hat, fa_hat, b_hat, fb_hat, d_hat, fd_hat = self.bracket(state, a_bar, fa_bar, b_bar, fb_bar, c_hat)
            x_root = self._root_if_converged(state, a_hat, fa_hat, b_hat, fb_hat, xtol_doubled)
            if x_root is not None:
                return x_root

            # --- 4.1.9 / 4.2.11 -----------------
            if b_hat - a_hat < self.mu * (b - a):
                a, fa, b, fb, d, fd = a_hat, fa_hat, b_hat, fb_hat, d_hat, fd_hat
                e, fe = d_bar, fd_bar
            else:
                e, fe = d_hat, fd_hat
                a, fa, b, fb, d, fd = self.bracket(state, a_hat, fa_hat, b_hat, fb_hat, 0.5 * (a_hat + b_hat))
                x_root = self._root_if_converged(state, a, fa, b, fb, xtol_doubled)
                if x_root is not None:
                    return x_root
            n += 1

    # --------------------------------------------------------------------------
    #  The paper's subroutines
    # --------------------------------------------------------------------------
    def bracket(
        self, state: SolveState, a: float, fa: float, b: float, fb: float, c: float
    ) -> tuple[float, float, float, float, float, float]:
        """Return ``(a_bar, f(a_bar), b_bar, f(b_bar), d, f(d))`` of ``bracket(a, b, c, a_bar, b_bar, d)``.

        This is ``bracket`` as the paper's section 6 modifies it, which takes these steps:

        - the margin: where ``[a, b]`` is at most ``4*delta`` wide, ``c`` becomes the midpoint; elsewhere, a ``c`` that
          lies less than ``2*delta`` inside ``[a, b]``, or outside it, moves to ``2*delta`` from the nearer bound. Here
          ``delta = lambda*tole(a, b)``, with the paper's absolute tolerance ``tol`` taken as ``state.xtol``;
        - ``f`` is evaluated at ``c``, and ``state.x_best`` is set to ``c``;
        - ``[a_bar, b_bar]`` is whichever of ``[a, c]`` and ``[c, b]`` holds the sign change, and ``d`` is the bound of
          ``[a, b]`` that ``c`` replaces.

        Section 6 ends the subroutine with its termination test; `_solve` instead calls `_root_if_converged` after each
        call of ``bracket``. Where ``f(c) = 0``, the paper terminates at ``c``; here ``c`` becomes ``a_bar``, and the
        shared stopping criterion ends the solve there.
        """
        # --- the margin of section 6 ------------
        delta = self.lambda_ * self.tole(a, fa, b, fb, state.xtol)
        if b - a <= 4.0 * delta:
            # The paper writes c = (a + b)/2; 0.5*(a + b) gives the same float64 value.
            c = 0.5 * (a + b)
        elif c <= a + 2.0 * delta:
            c = a + 2.0 * delta
        elif c >= b - 2.0 * delta:
            c = b - 2.0 * delta

        # --- the paper's label 10 ---------------
        fc = state.f(c)
        state.x_best = c
        # The condition compares the signs of the factors of the paper's test f(a)f(c) < 0. Because f(a) and f(b)
        # differ in sign, the else branch holds where the paper's second test, f(b)f(c) < 0, holds, and where f(c) = 0.
        if (fa < 0.0 < fc) or (fc < 0.0 < fa):
            return a, fa, c, fc, b, fb
        else:
            return c, fc, b, fb, a, fa

    def tole(self, a: float, fa: float, b: float, fb: float, tol: float) -> float:
        """Return ``tole(a, b) = 2*|u|*macheps + tol`` of the paper's section 6.

        ``u`` is the bound with the smaller ``|f|``. On a tie, which the paper leaves open, ``u`` is ``b``, by the rule
        of step 4.1.5, which picks ``u`` from the same 2 bounds.
        """
        if abs(fa) < abs(fb):
            u = a
        else:
            u = b
        return 2.0 * abs(u) * self.macheps + tol

    @staticmethod
    def newton_quadratic(a: float, fa: float, b: float, fb: float, d: float, fd: float, k: int) -> float:
        """Return ``r`` of the subroutine ``Newton-Quadratic(a, b, d, r, k)`` of the paper's section 2.

        ``r`` approximates the zero in ``[a, b]`` of ``P``, the quadratic interpolation through ``a``, ``b`` and ``d``:
        ``P(x) = f(a) + f[a, b]*(x - a) + f[a, b, d]*(x - a)*(x - b)``, with ``A = f[a, b, d]`` and ``B = f[a, b]``.

        Where ``A = 0``, ``P`` is a line, and ``r`` is its zero ``a - f(a) / B``. Elsewhere, ``r`` is the result of
        ``k`` Newton steps on ``P``, the paper's equation (4), starting from ``a`` where ``A*f(a) > 0``, and from ``b``
        otherwise.

        The subroutine's ``k`` is its number of Newton steps, not the solver's ``k``. The subroutine assumes that ``d``
        lies outside ``[a, b]``, with ``f(d)`` of the sign of ``f`` at the nearer bound, which ``bracket`` ensures.

        In exact arithmetic, the derivative of ``P`` never vanishes on the Newton steps: they start from the bound where
        ``P`` and its second derivative have the same sign, so they approach the zero of ``P`` from that side. The
        subroutine adds no guard there.

        Raises:
            ZeroDivisionError: If ``d`` equals ``a`` or ``b``, or if rounding makes ``B`` or the derivative of ``P`` 0.
        """
        # A = f[a, b, d] = (f[b, d] - f[a, b]) / (d - a) and B = f[a, b].
        B = (fb - fa) / (b - a)  # noqa: N806 — the paper's name
        A = ((fd - fb) / (d - b) - B) / (d - a)  # noqa: N806 — the paper's name
        if A == 0.0:
            return a - fa / B
        else:
            # The condition compares the signs of the factors of the paper's test A f(a) > 0; neither factor is 0 here.
            if (A > 0.0) == (fa > 0.0):
                r = a
            else:
                r = b
            for _ in range(k):
                # The Newton step of the paper's equation (4) computes
                # r_i = r_(i-1) - P(r_(i-1)) / (B + A*(2*r_(i-1) - a - b)).
                r = r - (fa + B * (r - a) + A * (r - a) * (r - b)) / (B + A * (2.0 * r - a - b))
            return r

    @staticmethod
    def ipzero(a: float, fa: float, b: float, fb: float, c: float, fc: float, d: float, fd: float) -> float:
        """Return ``x_bar`` of the subroutine ``ipzero(a, b, c, d, x_bar)`` of the paper's section 3.

        ``x_bar = IP(0)`` is the zero of ``IP``, the inverse cubic interpolation through ``a``, ``b``, ``c`` and ``d``,
        which gives x as a cubic in ``f``. The parameters keep the subroutine's own names: the algorithms call it with
        ``a_n``, ``b_n``, ``d_n`` and ``e_n`` as ``a``, ``b``, ``c`` and ``d``. The 4 function values must differ
        pairwise, which the algorithms check before they call ``ipzero``, so no denominator is 0.
        """
        Q11 = (c - d) * (fc / (fd - fc))  # noqa: N806 — the paper's name
        Q21 = (b - c) * (fb / (fc - fb))  # noqa: N806 — the paper's name
        Q31 = (a - b) * (fa / (fb - fa))  # noqa: N806 — the paper's name
        D21 = (b - c) * (fc / (fc - fb))  # noqa: N806 — the paper's name
        D31 = (a - b) * (fb / (fb - fa))  # noqa: N806 — the paper's name
        Q22 = (D21 - Q11) * (fb / (fd - fb))  # noqa: N806 — the paper's name
        Q32 = (D31 - Q21) * (fa / (fc - fa))  # noqa: N806 — the paper's name
        D32 = (D31 - Q21) * (fc / (fc - fa))  # noqa: N806 — the paper's name
        Q33 = (D32 - Q22) * (fa / (fd - fa))  # noqa: N806 — the paper's name
        return a + (Q31 + Q32 + Q33)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _has_2_equal_values(f1: float, f2: float, f3: float, f4: float) -> bool:
        """Return whether 2 of the 4 values are equal, which the paper tests as ``prod_(i != j) (f_i - f_j) = 0``."""
        return f1 in (f2, f3, f4) or f2 in (f3, f4) or f3 == f4

    def _root_if_converged(
        self, state: SolveState, a: float, fa: float, b: float, fb: float, xtol_doubled: float
    ) -> float | None:
        """Return the root estimate if the solve ends at the interval that ``bracket`` returned, or ``None``.

        ``[a, b]`` is that interval. ``state`` is not used here: the test suite overrides this method with the paper's
        termination test, to reproduce the paper's published counts, and that test computes ``tole(a, b)`` with
        ``tol = state.xtol``.
        """
        return interval_root_if_converged(a, fa, b, fb, xtol_doubled)
