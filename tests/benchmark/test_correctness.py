"""`is_solution_correct` looks for a proof that a root lies within `xtol` of `x_found`, in a fixed order of points."""

import math

import pytest

from sunnbear._core.benchmark.correctness import CORRECTNESS_CHECK_MAX_FEVALS, is_solution_correct


# ==================================================================================================
#  Test-local function
# ==================================================================================================
class _RecordingFunction:
    """`_RecordingFunction` wraps a function and records every point at which it is evaluated."""

    def __init__(self, f) -> None:
        self._f = f
        self.xs: list[float] = []

    def __call__(self, x: float) -> float:
        self.xs.append(x)
        return self._f(x)


def _narrow_dip(x: float) -> float:
    """Return `(x - 0.25)^2 - 1e-6`, which is positive at 0 and ±1 and negative only on the dip (0.249, 0.251)."""
    return (x - 0.25) ** 2 - 1e-6


# ==================================================================================================
#  Proofs
# ==================================================================================================
@pytest.mark.parametrize(
    "x_found, n_fevals_expected",
    [
        (0.3, 1),  # f(x_found) is exactly zero.
        (0.3 + 0.5e-3, 2),  # f(x_found) > 0 and f(x_found - xtol) < 0.
        (0.3 - 0.5e-3, 3),  # f(x_found) < 0 and f(x_found - xtol) < 0, then f(x_found + xtol) > 0.
    ],
)
def test_a_correct_answer_is_proven_by_the_first_3_points(x_found, n_fevals_expected):
    """An answer within `xtol` of the root of a monotone function is proven by `x_found` and `x_found ± xtol`."""
    # --- arrange ----------------------
    f = _RecordingFunction(lambda x: x - 0.3)

    # --- act --------------------------
    is_correct = is_solution_correct(f=f, x_found=x_found, xtol=1e-3, seed=1)

    # --- assert -----------------------
    assert is_correct
    assert len(f.xs) == n_fevals_expected


def test_a_candidate_point_within_xtol_proves_what_the_first_3_points_miss():
    """A candidate point in the dip gives the sign change on the 4th evaluation; the candidate point 1.25 is skipped."""
    # --- arrange ----------------------
    f = _RecordingFunction(_narrow_dip)

    # --- act --------------------------
    is_correct = is_solution_correct(f=f, x_found=0.0, xtol=1.0, seed=1, candidate_points=[1.25, 0.25])

    # --- assert -----------------------
    assert is_correct
    assert f.xs == [0.0, -1.0, 1.0, 0.25]


def test_random_points_find_a_sign_change_that_the_fixed_points_miss():
    """Without candidate points, the random points reach the dip within `CORRECTNESS_CHECK_MAX_FEVALS` evaluations."""
    # --- arrange ----------------------
    f = _RecordingFunction(_narrow_dip)

    # --- act --------------------------
    is_correct = is_solution_correct(f=f, x_found=0.0, xtol=1.0, seed=1)

    # --- assert -----------------------
    assert is_correct
    assert 3 < len(f.xs) < CORRECTNESS_CHECK_MAX_FEVALS


def test_a_failed_evaluation_proves_nothing_but_counts():
    """NaN at `x_found` and an exception at `x_found - xtol` prove nothing, so the proof needs more than 3 points."""

    # --- arrange ----------------------
    def f_raw(x: float) -> float:
        if x == 0.3:
            return math.nan
        elif x == 0.3 - 1e-3:
            raise ZeroDivisionError
        else:
            return x - 0.3 + 0.5e-3  # The root lies at 0.2995, within xtol of 0.3.

    f = _RecordingFunction(f_raw)

    # --- act --------------------------
    is_correct = is_solution_correct(f=f, x_found=0.3, xtol=1e-3, seed=1)

    # --- assert -----------------------
    assert is_correct
    assert f.xs[:3] == [0.3, 0.3 - 1e-3, 0.3 + 1e-3]
    assert len(f.xs) > 3


# ==================================================================================================
#  Wrong answers and the random points
# ==================================================================================================
def test_a_wrong_answer_spends_the_whole_limit():
    """With the root far beyond `xtol`, no proof exists, so all `CORRECTNESS_CHECK_MAX_FEVALS` evaluations are spent."""
    # --- arrange ----------------------
    f = _RecordingFunction(lambda x: x - 10.0)

    # --- act --------------------------
    is_correct = is_solution_correct(f=f, x_found=0.0, xtol=1.0, seed=1)

    # --- assert -----------------------
    assert not is_correct
    assert len(f.xs) == CORRECTNESS_CHECK_MAX_FEVALS


def test_the_random_points_stay_within_xtol_and_alternate_sides():
    """Every random point lies within `xtol` of `x_found`, first below it, then above, and so on."""
    # --- arrange ----------------------
    f = _RecordingFunction(lambda x: x - 10.0)

    # --- act --------------------------
    is_solution_correct(f=f, x_found=2.0, xtol=0.5, seed=1)

    # --- assert -----------------------
    random_points = f.xs[3:]
    assert all(abs(x - 2.0) <= 0.5 for x in random_points)
    assert all((x < 2.0) == (i % 2 == 0) for i, x in enumerate(random_points))


@pytest.mark.parametrize("seed_other, is_equal_expected", [(1, True), (2, False)])
def test_the_random_points_follow_the_seed(seed_other, is_equal_expected):
    """The same seed gives the same points, so the verdict is reproducible; another seed gives other points."""
    # --- arrange ----------------------
    f_first = _RecordingFunction(lambda x: x - 10.0)
    f_second = _RecordingFunction(lambda x: x - 10.0)

    # --- act --------------------------
    is_solution_correct(f=f_first, x_found=0.0, xtol=1.0, seed=1)
    is_solution_correct(f=f_second, x_found=0.0, xtol=1.0, seed=seed_other)

    # --- assert -----------------------
    assert (f_first.xs == f_second.xs) is is_equal_expected


@pytest.mark.parametrize("xtol", [0.0, -1.0, math.inf, math.nan])
def test_rejects_a_tolerance_that_is_not_positive_and_finite(xtol):
    """`is_solution_correct` raises `ValueError` for a zero, negative or non-finite `xtol`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="positive and finite"):
        is_solution_correct(f=lambda x: x, x_found=0.0, xtol=xtol, seed=1)
