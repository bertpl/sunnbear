"""These tests assert 3 things about `Ridders`:

- its name and version;
- that its arithmetic is counted;
- that it rejects an unknown variant.
"""

import pytest

from sunnbear.solvers import Ridders, RiddersVariant
from tests.solvers.example_functions import cubic


def test_an_unknown_variant_is_rejected():
    """A value that is not a `RiddersVariant` raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="'original'"):
        Ridders(variant="original")  # ty: ignore[invalid-argument-type] — the test passes a wrong value


def test_name_version_and_that_its_arithmetic_is_counted():
    """`Ridders` is named ``ridders``, at version 1, and its arithmetic, square roots included, is flop-counted."""
    # --- act --------------------------
    result = Ridders(variant=RiddersVariant.SCIPY).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Ridders.name, Ridders.version) == ("ridders", 1)
    assert result.flop_counts.SQRT > 0
