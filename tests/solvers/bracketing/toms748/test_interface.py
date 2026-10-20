"""These tests assert the following about `TOMS748`:

- its name and version;
- that its arithmetic is flop-counted, for both ``k``;
- that it rejects a ``k`` other than 1 or 2.
"""

import functools

import pytest
from counted_float import FlopCountingContext, Verbosity

from sunnbear._core.solvers.core import solver as solver_module
from sunnbear.solvers import TOMS748, SolveStatus
from tests.solvers.example_functions import cubic


def test_name_and_version():
    """`TOMS748` is named ``toms748``, at version 3."""
    # --- assert -----------------------
    assert (TOMS748.name, TOMS748.version) == ("toms748", 3)


@pytest.mark.parametrize("k", [1, 2])
def test_its_arithmetic_is_flop_counted(monkeypatch, k: int):
    """With counted-float set to raise at each operation that it cannot count, a solve of `TOMS748` still
    converges, and its flop count is not empty.

    `Solver.solve` opens its own flop-counting context, so the test patches that context to raise. A raised error would
    make `Solver.solve` report ``SOLVER_ERROR``, so a ``CONVERGED`` status shows that no operation went uncounted.
    """
    # --- arrange ----------------------
    monkeypatch.setattr(
        solver_module, "FlopCountingContext", functools.partial(FlopCountingContext, verbosity=Verbosity.ERROR)
    )

    # --- act --------------------------
    result = TOMS748(k=k).solve(cubic, 1.0, 2.0, xtol=1e-10, max_fevals=40)

    # --- assert -----------------------
    assert result.status is SolveStatus.CONVERGED
    assert result.flop_counts.total_count() > 0


@pytest.mark.parametrize("k", [0, 3])
def test_a_k_other_than_1_or_2_is_rejected(k: int):
    """A ``k`` other than 1 or 2 raises a `ValueError` that names it."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=f"k={k}"):
        TOMS748(k=k)
