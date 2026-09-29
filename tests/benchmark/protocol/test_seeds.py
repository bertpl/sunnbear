"""`derive_seed` gives a fixed 64-bit seed per root seed, purpose, test function and Monte Carlo sample."""

import pytest

from sunnbear._core.benchmark.protocol.seeds import SeedPurpose, derive_seed

_KWARGS = {
    "root_seed": 42,
    "purpose": SeedPurpose.CORRECTNESS_CHECK,
    "function_id": "f2.1.1[p1=0.2]",
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
        {"function_id": "f2.1.1[p1=0.3]"},
        {"mc_sample_idx": 8},
    ],
)
def test_changing_any_value_changes_the_seed(changed_kwargs):
    """A different root seed, test function or Monte Carlo sample gives a different seed within `[0, 2^64)`."""
    # --- act --------------------------
    seed = derive_seed(**(_KWARGS | changed_kwargs))

    # --- assert -----------------------
    assert seed != derive_seed(**_KWARGS)
    assert 0 <= seed < 2**64
