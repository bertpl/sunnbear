"""`is_bisection_count_exact` is true only when `Bisection` converges in exactly `DEFAULT_N_BISECTION_FEVALS`
evaluations at every tuple."""

import pytest

from sunnbear._core.benchmark.suites.pipeline.stages.s2_candidate_validation.check3_bisection_count import (
    is_bisection_count_exact,
)
from sunnbear._core.problems.core import FormulaRegistry
from tests.benchmark.suites.pipeline.stages.s2_candidate_validation.example_formulas import define_formula_cls


@pytest.mark.parametrize(
    "xc_fun, is_exact_expected",
    [
        # the offset 1 / 3 keeps the root off bisection's midpoints, so no solve ends early at an exact 0
        pytest.param(lambda x, c: x - c - 1 / 3, True, id="simple_root"),
        # bisection ends early at a midpoint inside the band where f is exactly 0
        pytest.param(lambda x, c: 0.0 if abs(x - c) < 0.01 else x - c, False, id="band_of_exact_zeros"),
        # f is NaN at the first midpoint, so bisection ends with a status other than converged
        pytest.param(lambda x, c: x - c if abs(x) == 1.0 else float("nan"), False, id="nan_between_the_bounds"),
    ],
)
def test_the_check_accepts_only_a_problem_with_bisection_s_exact_count_at_every_tuple(
    isolated_formula_registry, xc_fun, is_exact_expected
):
    """A simple root passes; a band of exact zeros or a solve that does not converge fails the check."""
    # --- arrange ----------------------
    define_formula_cls((99, 911), xc_fun, -1.0, 1.0)
    problem = FormulaRegistry.candidate_from_id("f99.911").calibrated(c_min=-0.5, c_max=0.5)

    # --- act --------------------------
    is_exact = is_bisection_count_exact(problem)

    # --- assert -----------------------
    assert is_exact is is_exact_expected
