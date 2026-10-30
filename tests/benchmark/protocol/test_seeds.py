"""`derive_seed` gives a fixed 64-bit seed per root seed, purpose, test problem and Monte Carlo sample."""

import pytest

from sunnbear._core.benchmark.protocol.seeds import SeedPurpose, derive_seed

_KWARGS = {
    "root_seed": 42,
    "purpose": SeedPurpose.CORRECTNESS_CHECK,
    "problem_id": "f2.1.1[p1=0.2]",
    "mc_sample_idx": 7,
}


def test_the_seed_of_known_values_is_fixed():
    """The seed for a fixed set of arguments must equal a stored value, so a change to how seeds are computed fails.

    Such a change would make past runs irreproducible.
    """
    # --- act / assert -----------------
    assert derive_seed(**_KWARGS) == 7745312542909566469


@pytest.mark.parametrize(
    "changed_kwargs",
    [
        {"root_seed": 43},
        {"problem_id": "f2.1.1[p1=0.3]"},
        {"mc_sample_idx": 8},
        {"problem_id": None, "mc_sample_idx": None},
    ],
)
def test_changing_any_value_changes_the_seed(changed_kwargs):
    """A different root seed, test problem or Monte Carlo sample gives a different seed within `[0, 2^64)`, and so does
    leaving out both the test problem and the Monte Carlo sample."""
    # --- act --------------------------
    seed = derive_seed(**(_KWARGS | changed_kwargs))

    # --- assert -----------------------
    assert seed != derive_seed(**_KWARGS)
    assert 0 <= seed < 2**64
