"""These tests assert the following about `Brent`:

- its name and version;
- that the arithmetic of both variants is counted;
- that it rejects an unknown variant.
"""

import pytest

from sunnbear.solvers import Brent, BrentVariant
from tests.solvers.example_functions import cubic


def test_an_unknown_variant_is_rejected():
    """A value that is not a `BrentVariant` raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="'quadratic'"):
        Brent(variant="quadratic")  # ty: ignore[invalid-argument-type] — the test passes a wrong value


@pytest.mark.parametrize("variant", BrentVariant)
def test_name_version_and_that_its_arithmetic_is_counted(variant):
    """`Brent` is named ``brent``, at version 2, and the arithmetic of each variant is flop-counted."""
    # --- act --------------------------
    result = Brent(variant=variant).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Brent.name, Brent.version) == ("brent", 2)
    assert result.flop_counts.total_count() > 0
