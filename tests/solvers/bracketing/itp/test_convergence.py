"""These tests assert that `ITP` converges to a root of the test functions, and that its paper_experiments variant
with slack keeps within its bound on the iteration count on the functions of the paper."""

import pytest

from sunnbear.solvers import ITP, ITPVariant, SolveStatus
from tests.solvers.example_functions import CUBIC_ROOT, cubic, decreasing_cubic

from .paper_problems import N_BISECTION, PAPER_TABLE_1, XTOL


@pytest.mark.parametrize("name", PAPER_TABLE_1)
def test_the_paper_experiments_variant_with_slack_stays_within_n_max_on_the_functions_of_the_paper(name):
    """On every function of the paper's Table 1, the paper_experiments variant with ``n_slack = 4`` takes at most
    ``n_max = 34 + 4`` iterations.

    This holds on these functions only: on harder ones, rounding errors can make this variant go past ``n_max`` too.
    """
    # --- arrange ----------------------
    f, _ = PAPER_TABLE_1[name]

    # --- act --------------------------
    result = ITP(n_slack=4, variant=ITPVariant.PAPER_EXPERIMENTS).solve(f, -1.0, 1.0, xtol=XTOL, max_fevals=100)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.n_fevals - 2 <= N_BISECTION + 4


@pytest.mark.parametrize("f", [cubic, decreasing_cubic])
def test_a_smooth_function_converges_to_its_root(f):
    """On `cubic`, which increases, and `decreasing_cubic`, which decreases, `ITP` converges within ``xtol`` of the
    root."""
    # --- act --------------------------
    result = ITP(n_slack=4, variant=ITPVariant.PAPER_EXPERIMENTS).solve(f, 1.0, 2.0, xtol=1e-10, max_fevals=60)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert abs(result.x - CUBIC_ROOT) <= 1e-10
