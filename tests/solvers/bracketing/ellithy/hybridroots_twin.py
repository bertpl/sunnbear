"""`EllithyHybridrootsTwin` runs the authors' package hybridroots as a `Solver`, so `Ellithy` can be tested against
it."""

import hybridroots

from sunnbear.solvers import EllithyVariant, Interval, IntervalBound
from tests.solvers.twins import StoppingWrappedFunction, TwinSolver

# Each variant maps to the function of hybridroots that implements its method.
_HYBRIDROOTS_FUNCTIONS = {
    EllithyVariant.BF: hybridroots.mpbf,
    EllithyVariant.BFMS: hybridroots.mpbfms,
    EllithyVariant.TF: hybridroots.mptf,
    EllithyVariant.TFMS: hybridroots.mptfms,
}


class EllithyHybridrootsTwin(TwinSolver):
    """`EllithyHybridrootsTwin` hands the interval to the function of hybridroots that implements the twin's variant,
    and returns the root estimate where `Ellithy`, in the same variant, would stop.

    hybridroots 1.0.1 is the authors' package of the 4 methods of Ellithy (2026): its functions ``mpbf``, ``mpbfms``,
    ``mptf`` and ``mptfms`` follow Algorithms 1 to 4 of the article, with its formulas in its order of operations. Each
    stops once ``|f(x)| <= tol`` at an x-value that its algorithm tests. The twin passes a negative ``tol``, so that
    hybridroots never stops by that test, and stops only where `Ellithy` would.

    `TwinSolver`'s version of `_root_if_sunnbear_solver_stops` checks the stopping criterion after every evaluation, on
    the initial interval split at every evaluated x-value. `Ellithy` differs from that in 3 ways:

    - it checks the stopping criterion only at the points that its class docstring lists;
    - it never splits its interval at the probe ``x_FP + delta`` or at a rejected ``x_S``;
    - it splits its interval at ``x2`` only where ``x1`` replaced the lower bound.

    So the twin's version replays the interval of `Ellithy` from the solve's initial interval, which
    `StoppingWrappedFunction` passes it for that purpose.

    The twin deviates from exact agreement in these declared ways:

    - hybridroots evaluates both interval bounds again before its first iteration;
    - hybridroots tests the sign of a product, such as ``fa*f(x) < 0``, where `Ellithy` compares the signs; the 2 differ
      only where the product underflows to 0, which no compared test case reaches;
    - hybridroots moves every denominator whose magnitude is below ``1e-15`` by ``1e-15`` away from 0, where `Ellithy`
      adds ``1e-15`` only to a modified-secant denominator of exactly 0; no compared test case reaches such a
      denominator.
    """

    name = "ellithy_hybridroots_twin"
    version = 1
    n_reevaluated_bounds = 2

    def __init__(self, *, variant: EllithyVariant) -> None:
        """Take the variant of the twin's `Ellithy` config."""
        self.variant = variant

    def _run_reference(self, f: StoppingWrappedFunction, a: float, b: float, xtol: float) -> None:
        """Run the function of hybridroots for the variant, with a negative ``tol``, which disables its own stopping
        test on ``|f(x)|``."""
        _HYBRIDROOTS_FUNCTIONS[self.variant](f, a, b, tol=-1.0)

    def _root_if_sunnbear_solver_stops(
        self,
        initial_interval: Interval,
        interval_split_at_evaluations: Interval,
        evaluations: list[tuple[float, float]],
        xtol: float,
    ) -> float | None:
        """Return the root estimate if `Ellithy` stops after the last of ``evaluations``, or ``None`` if it continues.

        `Ellithy` stops by the shared stopping criterion, checked on its own interval, which `_replay_interval`
        rebuilds; ``interval_split_at_evaluations`` is not used.
        """
        replayed_interval, is_stopping_criterion_checked = self._replay_interval(initial_interval, evaluations)
        if is_stopping_criterion_checked and replayed_interval.is_converged(2.0 * xtol):
            return replayed_interval.root()
        else:
            return None

    def _replay_interval(  # noqa: C901 — the replay follows the loop of `Ellithy._solve` phase by phase
        self, initial_interval: Interval, evaluations: list[tuple[float, float]]
    ) -> tuple[Interval, bool]:
        """Return the interval of `Ellithy` after the last of ``evaluations``, and whether `Ellithy` checks its stopping
        criterion right after that evaluation.

        The replay follows the phases of `Ellithy._solve` through ``evaluations``. An iteration evaluates ``x_S`` only
        where ``x_S`` lies inside the interval, so the replay computes ``x_S`` from ``x_FP`` and the probe, as `Ellithy`
        does, to tell whether the next evaluation is ``x_S`` or the next iteration's first x-value.
        """
        is_bisection = self.variant.is_bisection
        has_secant_step = self.variant.has_secant_step
        replayed_interval = initial_interval
        n_evaluations = len(evaluations)
        i = 0  # i is the index of the next evaluation in the replay
        while True:
            # --- phase 1 ------------------------
            if is_bisection:
                x_b, fx_b = evaluations[i]
                i += 1
                replayed_interval = replayed_interval.split_at(x_b, fx_b)
                if i == n_evaluations:
                    return replayed_interval, self.variant is EllithyVariant.BF
            else:
                if i + 1 == n_evaluations:
                    return replayed_interval, False  # Only x1 is evaluated; x2 follows before any update.
                (x1, fx1), (x2, fx2) = evaluations[i : i + 2]
                i += 2
                replayed_interval = replayed_interval.split_at(x1, fx1)
                if replayed_interval.last_replaced_bound is IntervalBound.LOWER and not replayed_interval.is_fa_zero:
                    replayed_interval = replayed_interval.split_at(x2, fx2)
                if i == n_evaluations:
                    return replayed_interval, True

            # --- phase 2 ------------------------
            x_fp, fx_fp = evaluations[i]
            i += 1
            replayed_interval = replayed_interval.split_at(x_fp, fx_fp)
            if i == n_evaluations:
                return replayed_interval, True

            # --- phase 3 ------------------------
            if has_secant_step:
                _, f_probe = evaluations[i]
                i += 1
                if i == n_evaluations:
                    return replayed_interval, False
                # The step and its guard against a zero denominator are those of `Ellithy`.
                delta = 1e-8 * max(1.0, abs(x_fp)) + 1e-15
                try:
                    x_s = x_fp - (delta * fx_fp) / (f_probe - fx_fp)
                except ZeroDivisionError:
                    x_s = x_fp - (delta * fx_fp) / ((f_probe - fx_fp) + 1e-15)
                if replayed_interval.a < x_s < replayed_interval.b:
                    # The evaluation holds x_S, which hybridroots computes by the same formula.
                    x_s, fx_s = evaluations[i]
                    i += 1
                    is_accepted = abs(fx_s) < abs(fx_fp)
                    if is_accepted:
                        replayed_interval = replayed_interval.split_at(x_s, fx_s)
                    if i == n_evaluations:
                        return replayed_interval, is_accepted
