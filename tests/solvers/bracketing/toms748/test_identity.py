"""These tests assert 3 things about `TOMS748`:

- its name and version;
- that its arithmetic is counted;
- that it rejects a ``k`` other than 1 or 2.
"""

import pytest

from sunnbear.solvers import TOMS748
from tests.solvers.example_functions import cubic


def test_a_k_other_than_1_or_2_is_rejected():
    """A ``k`` other than 1 or 2 raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="3"):
        TOMS748(k=3)


def test_identity_and_that_its_arithmetic_is_counted():
    """`TOMS748` is named ``toms748``, at version 1, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = TOMS748(k=1).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (TOMS748.name, TOMS748.version) == ("toms748", 1)
    assert result.flop_counts.total_count() > 0
