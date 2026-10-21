"""These tests assert the following about `TOMS748`:

- its name and version;
- that the arithmetic of both algorithms is counted;
- that it rejects a ``k`` other than 1 or 2.
"""

import pytest

from sunnbear.solvers import TOMS748
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize("k", [1, 2])
def test_name_version_and_that_its_arithmetic_is_counted(k: int):
    """`TOMS748` is named ``toms748``, at version 3, and the arithmetic of both algorithms is flop-counted."""
    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (TOMS748.name, TOMS748.version) == ("toms748", 3)
    assert result.flop_counts.total_count() > 0


@pytest.mark.parametrize("k", [0, 3])
def test_a_k_other_than_1_or_2_is_rejected(k: int):
    """A ``k`` other than 1 or 2 raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=f"k={k}"):
        TOMS748(k=k)
