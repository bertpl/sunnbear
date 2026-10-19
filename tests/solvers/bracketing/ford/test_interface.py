"""These tests assert the following about `Ford`:

- its name and version;
- that the arithmetic of every variant is counted;
- that it rejects an unknown variant.
"""

import pytest

from sunnbear.solvers import Ford, FordVariant
from tests.solvers.example_functions import cubic


def test_an_unknown_variant_is_rejected():
    """A value that is not a `FordVariant` raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="'method_2'"):
        Ford(variant="method_2")  # ty: ignore[invalid-argument-type] — the test passes a wrong value


@pytest.mark.parametrize("variant", FordVariant)
def test_name_version_and_that_its_arithmetic_is_counted(variant):
    """`Ford` is named ``ford``, at version 1, and the arithmetic of each variant is flop-counted."""
    # --- act --------------------------
    result = Ford(variant=variant).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Ford.name, Ford.version) == ("ford", 1)
    assert result.flop_counts.total_count() > 0
