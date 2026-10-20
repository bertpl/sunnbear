"""These tests assert that the phases of each variant of `Ellithy` follow the article's algorithms, and how `Ellithy`
handles a zero at ``x1``, a zero denominator in the modified-secant step, and a probe outside the initial interval."""

import pytest

from sunnbear.solvers import Ellithy, EllithyVariant, SolveStatus
from tests.solvers.example_functions import cubic


def _quadratic(x: float) -> float:
    """Return ``x^2 - 2``, on which each phase can be computed by hand."""
    return x * x - 2.0


@pytest.mark.parametrize("variant", [EllithyVariant.BF, EllithyVariant.BFMS])
def test_the_bisection_variants_evaluate_the_midpoint_then_the_false_position(variant):
    """The bisection variants evaluate the midpoint, then the false position on the half that holds the sign change.

    On `_quadratic` over ``[0, 2]``, ``f(1) = -1``, so 1 replaces the lower bound, and the false position on ``[1, 2]``
    is ``(1*2 - 2*(-1)) / (2 - (-1)) = 4/3``.
    """
    # --- act --------------------------
    result = Ellithy(variant=variant).solve(_quadratic, 0.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.evaluated_x_values[2:4] == (1.0, 4.0 / 3.0)


@pytest.mark.parametrize("variant", [EllithyVariant.TF, EllithyVariant.TFMS])
@pytest.mark.parametrize(
    "a, b, x_fp",
    [(0.0, 2.0, 1.4), (1.0, 4.0, 4.0 / 3.0), (0.0, 3.0, 4.0 / 3.0)],
    ids=["upper_third", "lower_third", "middle_third"],
)
def test_the_trisection_variants_evaluate_both_thirds_then_the_false_position(variant, a, b, x_fp):
    """The trisection variants evaluate ``x1`` and ``x2``, then the false position on the third with the sign change.

    On `_quadratic`, the false position shows which third the variants kept:

    - over ``[0, 2]``, ``f`` is negative at both 2/3 and 4/3, so the interval becomes ``[4/3, 2]``, and the false
      position is ``(4/3*2 - 2*(-2/9)) / (2 - (-2/9)) = 7/5``;
    - over ``[1, 4]``, ``f(2) = 2`` is positive, so the interval becomes ``[1, 2]``, and the false position is 4/3;
    - over ``[0, 3]``, ``f(1) = -1`` and ``f(2) = 2``, so the interval becomes ``[1, 2]``, and the false position is
      4/3.
    """
    # --- act --------------------------
    result = Ellithy(variant=variant).solve(_quadratic, a, b, xtol=1e-9, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    third = (b - a) / 3.0
    assert result.evaluated_x_values[2:4] == (a + third, b - third)
    assert result.evaluated_x_values[4] == pytest.approx(x_fp, rel=1e-15)


@pytest.mark.parametrize(
    "variant, x_fp, x_newton",
    [(EllithyVariant.BFMS, 4.0 / 3.0, 17.0 / 12.0), (EllithyVariant.TFMS, 1.4, 1.4 + 1.0 / 70.0)],
)
def test_the_secant_variants_take_a_modified_secant_step_from_the_false_position(variant, x_fp, x_newton):
    """The secant variants evaluate the probe ``x_FP + delta``, then ``x_S``, which lies near Newton's step and
    replaces a bound.

    On `_quadratic` over ``[0, 2]``, the false position ``x_FP`` is 4/3 for ``"bfms"`` and 7/5 for ``"tfms"``, and
    ``delta = 1e-8*x_FP + 1e-15``. ``x_S`` lies within about ``delta`` of Newton's step ``x_FP - f(x_FP) / (2*x_FP)``,
    and ``|f(x_S)|`` is below ``|f(x_FP)|``, so ``x_S`` replaces the upper bound, and the next iteration starts on
    ``[x_FP, x_S]``.
    """
    # --- act --------------------------
    result = Ellithy(variant=variant).solve(_quadratic, 0.0, 2.0, xtol=1e-9, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    i_fp = 3 if variant is EllithyVariant.BFMS else 4
    x_fp_evaluated, probe, x_s, x_next = result.evaluated_x_values[i_fp : i_fp + 4]
    assert x_fp_evaluated == pytest.approx(x_fp, rel=1e-15)
    assert probe == x_fp_evaluated + (1e-8 * x_fp_evaluated + 1e-15)
    assert x_s == pytest.approx(x_newton, rel=1e-8)
    if variant is EllithyVariant.BFMS:
        assert x_next == 0.5 * (x_fp_evaluated + x_s)
    else:
        assert x_next == x_fp_evaluated + (x_s - x_fp_evaluated) / 3.0


@pytest.mark.parametrize("variant, n_fevals", [(EllithyVariant.BF, 3), (EllithyVariant.BFMS, 4)])
def test_bf_checks_its_stopping_criterion_after_the_bisection_and_bfms_does_not(variant, n_fevals):
    """``"bf"`` stops right after a bisection that leaves the interval narrow enough, ``"bfms"`` 1 evaluation later.

    On `cubic` over ``[1.3247, 1.3248]`` at ``xtol = 3e-5``, the bisection leaves an interval narrower than ``2*xtol``;
    Algorithm 2, of ``"bfms"``, has no test there, so ``"bfms"`` first evaluates the false position.
    """
    # --- act --------------------------
    result = Ellithy(variant=variant).solve(cubic, 1.3247, 1.3248, xtol=3e-5, max_fevals=10)

    # --- assert -----------------------
    assert (result.status, result.n_fevals) == (SolveStatus.CONVERGED, n_fevals)


@pytest.mark.parametrize("variant", [EllithyVariant.TF, EllithyVariant.TFMS])
def test_a_zero_at_x1_ends_the_solve_at_x1(variant):
    """The trisection variants return a zero at ``x1`` right after the trisection.

    On ``(x - 1)^2 * (x - 2.5)`` over ``[0, 3]``, ``x1 = 1`` is a root, and ``f(x2) = f(2) = -0.5`` has the sign of
    ``f(0)``, so the article's trisection update would move the lower bound to 2 and lose the root at 1.
    """
    # --- act --------------------------
    result = Ellithy(variant=variant).solve(
        lambda x: (x - 1.0) ** 2 * (x - 2.5), 0.0, 3.0, xtol=1e-9, max_fevals=60, history_enabled=True
    )

    # --- assert -----------------------
    assert result.evaluated_x_values == (0.0, 3.0, 1.0, 2.0)
    assert (result.status, result.x) == (SolveStatus.CONVERGED, 1.0)


def test_a_zero_secant_denominator_adds_eps_and_an_x_s_that_does_not_lower_f_is_rejected():
    """The modified-secant step adds ``eps`` to a denominator of 0, and rejects an ``x_S`` that does not lower ``|f|``.

    On a function that equals ``-1e-9`` for x below 1.9 and 1 from 1.9 up, over ``[0, 2]``, ``"bfms"`` evaluates the
    midpoint 1 and the false position ``x_FP``, just above 1. ``f`` is flat there, so ``f(x_FP + delta) - f(x_FP)``
    is 0, and the step divides by ``eps = 1e-15``; ``x_S`` then lies about 0.01 above ``x_FP``, inside the interval.
    ``|f(x_S)|`` equals ``|f(x_FP)|``, so the next iteration bisects ``[x_FP, 2]``.
    """

    # --- arrange ----------------------
    def f(x: float) -> float:
        if x < 1.9:
            return -1e-9
        else:
            return 1.0

    # --- act --------------------------
    result = Ellithy(variant=EllithyVariant.BFMS).solve(f, 0.0, 2.0, xtol=1e-6, max_fevals=7, history_enabled=True)

    # --- assert -----------------------
    x_b, x_fp, probe, x_s, x_next = result.evaluated_x_values[2:7]
    delta = 1e-8 * x_fp + 1e-15
    assert (x_b, probe) == (1.0, x_fp + delta)
    assert x_s == x_fp - (delta * -1e-9) / (0.0 + 1e-15)
    assert x_next == 0.5 * (x_fp + 2.0)


def test_an_x_s_outside_the_interval_is_not_evaluated():
    """An ``x_S`` outside the interval is not evaluated, and the next iteration starts.

    On a function that equals -1 for x below 1.9 and 1 from 1.9 up, over ``[0, 2]``, ``"bfms"`` evaluates the midpoint
    1, and the false position 1.5. ``f`` is flat there, so the step divides by ``eps = 1e-15``, and ``x_S``, about
    ``1.5e7`` above 1.5, lies outside the interval ``[1.5, 2]``: the next evaluation is the next iteration's midpoint,
    1.75.
    """

    # --- arrange ----------------------
    def f(x: float) -> float:
        if x < 1.9:
            return -1.0
        else:
            return 1.0

    # --- act --------------------------
    result = Ellithy(variant=EllithyVariant.BFMS).solve(f, 0.0, 2.0, xtol=1e-6, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    assert result.evaluated_x_values[2:6] == (1.0, 1.5, 1.5 + (1e-8 * 1.5 + 1e-15), 1.75)


@pytest.mark.parametrize("variant", [EllithyVariant.BFMS, EllithyVariant.TFMS])
def test_a_probe_outside_the_initial_interval_where_f_fails_ends_the_solve_as_diverged(variant):
    """Where ``f`` fails at a probe outside the initial interval, the solve ends as ``DIVERGED``, at the false position.

    On ``1e-18 - (1 - x)^2`` over ``[0.5, 1]``, a function that raises ``ValueError`` above 1, the false position of
    the first iteration is the upper bound 1, where ``|f|`` is 1e-18, so the probe ``1 + delta`` lies outside the
    initial interval.
    """

    # --- arrange ----------------------
    def f(x: float) -> float:
        if x > 1.0:
            raise ValueError("f is not defined above 1")
        else:
            return 1e-18 - (1.0 - x) ** 2

    # --- act --------------------------
    result = Ellithy(variant=variant).solve(f, 0.5, 1.0, xtol=1e-12, max_fevals=60, history_enabled=True)

    # --- assert -----------------------
    # The history holds the evaluations that returned a value; the count includes the failed evaluation at the probe.
    assert result.evaluated_x_values[-1] == 1.0
    assert result.n_fevals == len(result.history) + 1
    assert (result.status, result.x) == (SolveStatus.DIVERGED, 1.0)
