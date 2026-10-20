"""These tests assert the following about `Ellithy`:

- its name and version;
- that the arithmetic of every variant is counted;
- that it rejects an unknown variant.
"""

import pytest

from sunnbear.solvers import Ellithy, EllithyVariant
from tests.solvers.example_functions import cubic


def test_an_unknown_variant_is_rejected():
    """A value that is not an `EllithyVariant` raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="'bms'"):
        Ellithy(variant="bms")  # ty: ignore[invalid-argument-type] — the test passes a wrong value


@pytest.mark.parametrize("variant", EllithyVariant)
def test_name_version_and_that_its_arithmetic_is_counted(variant):
    """`Ellithy` is named ``ellithy``, at version 1, and the arithmetic of each variant, divisions included, is
    flop-counted."""
    # --- act --------------------------
    result = Ellithy(variant=variant).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Ellithy.name, Ellithy.version) == ("ellithy", 1)
    assert result.flop_counts.DIV > 0
