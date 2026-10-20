"""These tests assert the names and versions of `ModAB` and `ModABSafeguarded`, and that their arithmetic is
counted."""

import pytest

from sunnbear.solvers import ModAB, ModABSafeguarded
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize(
    "solver_cls, name, version",
    [(ModAB, "modab", 3), (ModABSafeguarded, "modab_safeguarded", 1)],
    ids=["ModAB", "ModABSafeguarded"],
)
def test_name_version_and_that_its_arithmetic_is_counted(solver_cls, name, version):
    """`ModAB` is named ``modab``, at version 3, and `ModABSafeguarded` ``modab_safeguarded``, at version 1; the
    arithmetic of each is flop-counted."""
    # --- act --------------------------
    result = solver_cls().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (solver_cls.name, solver_cls.version) == (name, version)
    assert result.flop_counts.total_count() > 0
