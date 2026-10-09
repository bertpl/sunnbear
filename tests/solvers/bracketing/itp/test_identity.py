"""These tests assert the name and version of `ITP`, that its arithmetic is counted, and that it rejects invalid
arguments."""

import pytest

from sunnbear.solvers import ITP, ITPVariant
from tests.solvers.example_functions import cubic


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"n_slack": -1, "variant": ITPVariant.PAPER_EXPERIMENTS}, "-1"),
        ({"n_slack": 0, "variant": "robust"}, "'robust'"),
    ],
)
def test_an_invalid_argument_is_rejected(kwargs, match):
    """A negative ``n_slack``, or a value that is not an `ITPVariant`, raises a `ValueError` that names the wrong
    value."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=match):
        ITP(**kwargs)


def test_identity_and_that_its_arithmetic_is_counted():
    """`ITP` has name ``itp`` and version 1, and its flop count includes the logarithm that sets ``n_bisection``."""
    # --- act --------------------------
    result = ITP(n_slack=4, variant=ITPVariant.PAPER_EXPERIMENTS).solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=40)

    # --- assert -----------------------
    assert (ITP.name, ITP.version) == ("itp", 1)
    assert result.flop_counts.LOG2 == 1
