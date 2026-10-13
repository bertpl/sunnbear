"""These tests assert 3 things about `ITP`:

- its name and version;
- that its arithmetic is counted;
- that it rejects invalid arguments.
"""

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


def test_name_version_and_that_its_arithmetic_is_counted():
    """`ITP` has name ``itp`` and version 2, and its flop count includes the logarithm that sets ``n_bisection`` and,
    in every iteration, the power ``2^(n_max - k)`` of the projection radius."""
    # --- act --------------------------
    result = ITP(n_slack=4, variant=ITPVariant.PAPER_EXPERIMENTS).solve(cubic, 1.0, 2.0, xtol=1e-6, max_fevals=40)

    # --- assert -----------------------
    n_iterations = result.n_fevals - 2
    assert (ITP.name, ITP.version) == ("itp", 2)
    assert result.flop_counts.LOG2 == 1
    assert n_iterations == result.flop_counts.POW
