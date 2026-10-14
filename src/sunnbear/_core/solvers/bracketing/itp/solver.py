"""`ITP` implements the ITP method: interpolation, truncated toward the midpoint and projected around it.

The rest of this docstring is the record of `ITP` under the solver implementation principles
(``IMPLEMENTATION_PRINCIPLES.md`` in the ``sunnbear._core.solvers`` package).

The names ``r``, ``n_max``, ``n_slack``, ``kappa_1``, ``kappa_2``, ``a0`` and ``b0`` are those of the class docstring
of `ITP`. The paper calls ``n_slack`` ``n0``.

Sources:
    - I - article:
      - Ia - article code: none;
      - Ib - article pseudocode: Oliveira and Takahashi (2020), Algorithm 1 in its Appendix B, and Algorithm 0 in its
        section 1, a bracketing algorithm in which a method, here ITP, chooses the x-value of each iteration, and
        which returns the final interval's midpoint;
      - Ic - article text: Oliveira and Takahashi (2020):
        - equations 13 to 16 in its section 2.1;
        - the constants of its experiments in section 3;
        - the advice in its Appendix B to lower the projection radius by a small margin and to clamp it at 0.
    - II - authors' code:
      - the authors' MATLAB code that produced the paper's experiments, shared on request: the steps of Algorithm 1,
        with a margin and a clamp at 0 on the projection radius.
    - III - third party:
      - the C# ITP in the supplementary code of Ganchovski et al. (2026): the steps of Algorithm 1 with ``n0 = 1``,
        ``kappa_1 = 0.2 / (b0 - a0)`` and ``kappa_2 = 2``, the projection radius clamped at 0, and a stopping rule
        with an absolute and a relative tolerance.
    - IV - own judgment:
      - the value 4 of ``n_slack`` in the secondary config `ITPPaperExperimentsSlack4Config`.

Source per aspect:
    Every aspect of the core config, `ITPPaperExperimentsSlack0Config`, follows Algorithm 1 of Oliveira and Takahashi
    (2020), except:
    - The projection radius follows the authors' code, which lowers Algorithm 1's radius ``r`` to
      ``max(0.99 * r - xtol / 2, 0)``, because the validation with Algorithm 1's radius is not convincing (P5): with
      it, 17 of Table 1's 24 counts match, and with the authors' radius, 23 match.
      - Appendix B suggests a margin and a clamp at 0, without the margin's amount.
    - The constants follow section 3, because Algorithm 1 takes them as inputs: ``kappa_2 = 2``, ``n0 = 0`` (the
      core config's ``n_slack``), and ``kappa_1 = 0.1`` on an x axis scaled to [-1, 1].
    - JUDGMENT-CALL: `ITP` keeps the problem's x axis and sets ``kappa_1 = 0.2 / (b0 - a0)`` for the initial interval
      ``[a0, b0]``, as the C# ITP does, so that ``f`` needs no change of variable; for ``kappa_2 = 2``, this choice of
      ``kappa_1`` gives, in exact arithmetic, the same x-values as ``kappa_1 = 0.1`` on the axis scaled to [-1, 1].
      - In float64, the x-values agree to about 1e-15 relative, yet in 26 of 126 solves of 8 functions the evaluation
        counts differ, by up to 24, mostly where the run on the scaled axis and the run on the problem's axis put an
        x-value within 2 ulps (units in the last place) of the root on opposite sides of it.
    - The returned x-value is the final interval's midpoint, the output of Algorithm 0, because Algorithm 1 returns the
      final interval. Algorithm 1 also requires ``f(a) < 0 < f(b)``; where ``f(a) > 0 > f(b)``, `ITP` accepts the
      interval, as Algorithm 0 does, and evaluates the same x-values as it would on ``-f``.
    - JUDGMENT-CALL: a function value of 0 at an initial interval bound ends the solve at that bound, as for every
      solver. Algorithm 1 excludes this case; the authors' code does not check for it, and on 5 functions with such a
      bound, that code ends within ``xtol`` of that bound after 4 or 5 more evaluations.
    - Translation of ``xtol`` (P7): ``xtol`` is Algorithm 1's ``epsilon``, which sets:
      - the projection radius, from which the authors' margin also subtracts ``xtol / 2``;
      - the stopping width ``2 * xtol``;
      - ``n_1/2``, the number of bisection iterations needed to reach that width.

Validation:
    - A - authors' results:
      - used: Table 1, the column "ITP": the core config reproduces 23 of the 24 counts exactly, and that of the step
        function within 1, which is convincing (P5).
        - On the step function, rounding in the interval bounds leaves the interval slightly wider than ``2 * xtol``
          after the ``n_max = 34`` iterations, so the solve takes 35, as a port of the authors' code does in float64;
          in exact arithmetic, it ends after 34, the table's count.
      - not used: Figures 2 to 5, which are plots; Figures 4 and 5 use 1000-bit arithmetic.
      - TBD: Table 2, and the rows "Global Average" and "Global Worst Case" of Table 1, which summarize Table 1's
        counts and which no test checks: the core config's counts reproduce every value in these rows and in Table 2's
        column "ITP", except the worst case, 35 against 34.
    - B - third-party results:
      - not used: the column "ITP" of Ganchovski et al. (2026), Table 2, because no config of `ITP` runs the paper's
        settings.
      - not used: the column "ITP" of Ganchovski and Traykov (2023), Table 2, because the paper does not state the
        settings of its ITP runs.
      - The docstring of the test package ``tests.solvers.bracketing.itp`` gives the details.
    - C - reference implementation:
      - not used: no implementation of ITP that a twin test could run exists: SciPy and mpmath have none, and the C#
        ITP needs a .NET runtime, which the tests do not have.

Variants:
    - `ITPPaperExperimentsSlack0Config`, variant ``"paper_experiments"`` with ``n_slack = 0``, is core (P8).
    - `ITPPaperPseudocodeSlack0Config` is secondary (P8): it keeps Algorithm 1's projection radius, which the core
      config replaces (P2, P5); with that radius, the 7 counts of Table 1 that differ take 1 to 19 iterations more.
    - `ITPPaperExperimentsSlack4Config` is secondary (P8): its ``n_slack = 4`` comes from IV - own judgment, and goes
      against P1, since section 3 and the authors' code use ``n0 = 0``, and the C# ITP uses 1.
      - PRINCIPLE-GAP (P8): no docstring says why ``n_slack`` is 4; P8 asks that each variant have a didactic reason,
        but does not say whether the value of a variant's parameter needs one. The code keeps 4.
      - The 4 extra iterations do not stop a solve from going past its ``n_max``, because rounding in the interval
        bounds can make a solve go past ``n_max`` for every ``n_slack``: on [-1, 1] with ``xtol = 1e-9``, Table 1's
        step function takes 35 iterations, against ``n_max = 34``.
"""

import math

from sunnbear._core.solvers.core import BracketingSolver, Interval

from .state import ITPState
from .variant import ITPVariant

# ``kappa_1`` and ``kappa_2`` are the truncation constants that the `ITP` docstring gives. ``kappa_1`` depends on
# the initial interval, so `ITP._solve` sets it per solve from `_KAPPA_1_TIMES_INITIAL_WIDTH`.
_KAPPA_1_TIMES_INITIAL_WIDTH = 0.2
_KAPPA_2 = 2


class ITP(BracketingSolver[ITPState]):
    """`ITP` implements the ITP method, in the variant of its paper's pseudocode or in that of its paper's experiments.

    The paper is Oliveira and Takahashi (2020). Each iteration evaluates 1 x-value, ``x_itp``, which it computes from
    the interval ``[a, b]`` and its midpoint ``x_half`` in 3 steps:

    - interpolation: ``x_f`` is where the chord through ``(a, f(a))`` and ``(b, f(b))`` crosses zero, as in regula
      falsi;
    - truncation: ``x_t`` is ``x_f`` moved toward ``x_half`` by ``delta = kappa_1 * (b - a)^kappa_2``, for 2
      constants ``kappa_1`` and ``kappa_2``, or ``x_half`` itself when ``x_f`` lies closer to ``x_half`` than
      ``delta``;
    - projection: ``x_itp`` is ``x_t``, or, when ``x_t`` lies farther than a radius ``r`` from ``x_half``, the x-value
      at distance ``r`` from ``x_half`` toward ``x_t``; the projection radius ``r`` is defined after this list.

    ``n_bisection = ceil(log2((b0 - a0) / (2 * xtol)))``, the paper's ``n_1/2``, is the iteration count of bisection
    on the initial interval ``[a0, b0]``.

    In iteration ``k``, counted from 0, the radius ``r = xtol * 2^(n_max - k) - (b - a) / 2`` keeps the solve within
    ``n_max = n_bisection + n_slack`` iterations.

    So, in exact arithmetic, the method needs at most ``n_slack`` iterations more than bisection, while it converges
    superlinearly on smooth functions. In floating point, once the interval nears the width that ``n_max`` allows,
    rounding errors in the bounds can leave it slightly wider than ``2 * xtol`` after iteration ``n_max``, so 1 or
    more iterations follow; this holds for every ``n_slack``.

    The constants follow the paper's experiments: ``kappa_2 = 2``, and ``kappa_1 = 0.2 / (b0 - a0)``, so that the
    first truncation moves ``x_f`` by at most 20 % of the initial width.

    ``variant``, a value of `ITPVariant`, picks the source of the projection radius ``r``:

    - ``"paper_pseudocode"``: ``r`` as the pseudocode of the paper's Appendix B states it.
    - ``"paper_experiments"``: ``r`` becomes ``max(0.99 * r - xtol / 2, 0)``, as in the authors' MATLAB code that
      produced the paper's experiments.

    The margin, the amount by which ``"paper_experiments"`` lowers ``r``, guards against rounding errors in ``r``, as
    the paper's Appendix B recommends in general terms; the margin makes solves that go past ``n_max`` rarer, but does
    not prevent them all.

    Under either variant, ``r`` can reach 0, and every later step is then the midpoint ``x_half``: under
    ``"paper_experiments"`` once ``0.99 * r`` falls to ``xtol / 2``, and under ``"paper_pseudocode"`` once a step lands
    at distance ``r`` from ``x_half`` and the interval keeps its larger part; in exact arithmetic ``r`` then stays 0.

    The interval, the stopping criterion and the root estimate are `BracketingSolver`'s: the solve ends once the
    interval is at most ``2 * xtol`` wide, as in the paper, and returns its midpoint, which then lies within ``xtol``
    of a root.

    References:
        - Oliveira, I. F. D. and Takahashi, R. H. C. (2020). An enhancement of the bisection method average
          performance preserving minmax optimality. ACM Transactions on Mathematical Software 47(1), article 5.
          ``"paper_pseudocode"`` follows the pseudocode in the paper's Appendix B, and the test suite reproduces the
          iteration counts in the paper's Table 1 with ``"paper_experiments"`` and ``n_slack = 0``.
          https://doi.org/10.1145/3423597
        - The authors' MATLAB code that produced the paper's experiments, which ``"paper_experiments"`` follows. The
          authors shared it on request; it is not published.
        - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
          Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. Its supplementary C# code, in the
          authors' repository https://github.com/Just-A-Random-Geek/ModAB-Root-Finding, holds an ITP with
          ``n_slack = 1`` that stops on an absolute and a relative tolerance, and its Table 2 holds the column "ITP",
          which the test suite does not reproduce. https://doi.org/10.3390/a19050332
        - Ganchovski, N. and Traykov, A. (2023). Modified Anderson-Björck's method for solving non-linear equations in
          structural mechanics. IOP Conference Series: Materials Science and Engineering 1276, 012010. Its Table 2
          holds the column "ITP", for runs whose settings the paper does not state.
          https://doi.org/10.1088/1757-899X/1276/1/012010
    """

    name = "itp"
    version = 2
    state_cls = ITPState

    def __init__(self, *, n_slack: int, variant: ITPVariant) -> None:
        """Configure the method.

        Args:
            n_slack: The paper's ``n_0``, the number of iterations that the solve may take beyond the iteration count
                of bisection.
            variant: The paper's source for the projection radius ``r``: ``"paper_pseudocode"`` uses ``r`` as the
                pseudocode states it, and ``"paper_experiments"`` lowers ``r`` by the margin of the authors' MATLAB
                code. A plain string such as ``"paper_experiments"`` works too.

        Raises:
            ValueError: If ``n_slack`` is negative, or ``variant`` is not a value of `ITPVariant`.
        """
        if n_slack < 0:
            raise ValueError(f"n_slack must be at least 0 (got {n_slack}).")
        self.n_slack = n_slack
        self.variant = ITPVariant(variant)

    def _solve(self, state: ITPState) -> float:
        """Set the solve's ``kappa_1`` and ``n_max`` on ``state``, then run `BracketingSolver`'s loop."""
        width = state.interval.width
        n_bisection = math.ceil(math.log2(width / (2.0 * state.xtol)))
        state.kappa_1 = _KAPPA_1_TIMES_INITIAL_WIDTH / width
        state.n_max = n_bisection + self.n_slack
        return super()._solve(state)

    def _next_x(self, state: ITPState, interval: Interval) -> float:
        """Return ``x_itp``, the chord's zero ``x_f`` truncated and projected as the class docstring says.

        Also advance the iteration counter ``state.k``, so 2 calls on the same interval return different x-values.
        """
        # --- interpolation ----------------------
        x_f = (interval.fb * interval.a - interval.fa * interval.b) / (interval.fb - interval.fa)

        # --- truncation -------------------------
        x_half = interval.midpoint
        x_half_minus_x_f = x_half - x_f
        if x_half_minus_x_f > 0.0:
            sigma = 1.0
        elif x_half_minus_x_f < 0.0:
            sigma = -1.0
        else:
            sigma = 0.0
        delta = state.kappa_1 * interval.width**_KAPPA_2
        if delta <= abs(x_half_minus_x_f):
            x_t = x_f + sigma * delta
        else:
            x_t = x_half

        # --- projection -------------------------
        # 2^(n_max - k) is an integer power of 2, which is integer arithmetic, not a flop.
        r = state.xtol * 2 ** (state.n_max - state.k) - 0.5 * interval.width
        state.k += 1
        if self.variant is ITPVariant.PAPER_EXPERIMENTS:
            # Apply the margin of the authors' MATLAB code; the class docstring describes its 2 effects.
            r = max(0.99 * r - 0.5 * state.xtol, 0.0)
        if abs(x_t - x_half) <= r:
            return x_t
        else:
            return x_half - sigma * r
