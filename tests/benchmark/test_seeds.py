"""`derive_seed` gives a fixed 64-bit seed per root seed, purpose, test function and sample."""

import pytest

from sunnbear._core.benchmark.seeds import SeedPurpose, derive_seed

_ARGS = (42, SeedPurpose.CORRECTNESS_CHECK, "f2.1.1[p1=0.2]", 7)


def test_the_seed_of_known_values_is_fixed():
    """The seed for a fixed set of arguments must equal a stored value, so a change to how seeds are computed fails.

    Such a change would make past runs irreproducible.
    """
    # --- act / assert -----------------
    assert derive_seed(*_ARGS) == 7745312542909566469


@pytest.mark.parametrize(
    "args",
    [
        (43, *_ARGS[1:]),
        (*_ARGS[:2], "f2.1.1[p1=0.3]", _ARGS[3]),
        (*_ARGS[:3], 8),
    ],
)
def test_changing_any_value_changes_the_seed(args):
    """A different root seed, test function or sample gives a different seed within `[0, 2^64)`."""
    # --- act --------------------------
    seed = derive_seed(*args)

    # --- assert -----------------------
    assert seed != derive_seed(*_ARGS)
    assert 0 <= seed < 2**64
