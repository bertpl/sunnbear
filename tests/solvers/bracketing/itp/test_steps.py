"""These tests assert that the individual steps of `ITP` follow its algorithm."""

from sunnbear.solvers import ITP, ITPVariant

from .paper_problems import N_BISECTION, PAPER_TABLE_1, XTOL


def test_the_paper_pseudocode_variant_ends_as_bisection_once_its_projection_radius_reaches_0():
    """On the paper's first polynomial, the projection radius of the paper_pseudocode variant reaches 0 and stays 0,
    so it takes bisection's 34 iterations; the paper_experiments variant keeps its projection radius above 0 and takes
    18."""
    # --- arrange ----------------------
    f, _ = PAPER_TABLE_1["polynomial_1"]

    # --- act --------------------------
    n_iterations = {
        variant: ITP(n_slack=0, variant=variant).solve(f, -1.0, 1.0, xtol=XTOL, max_fevals=100).n_fevals - 2
        for variant in ITPVariant
    }

    # --- assert -----------------------
    assert n_iterations == {ITPVariant.PAPER_PSEUDOCODE: N_BISECTION, ITPVariant.PAPER_EXPERIMENTS: 18}
