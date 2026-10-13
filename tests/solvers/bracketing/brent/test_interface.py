"""These tests assert the name and version of `Brent`, and that its arithmetic is counted as in Brent's Algol 60
procedure."""

from sunnbear.solvers import Brent
from tests.solvers.example_functions import cubic


def test_name_version_and_that_its_arithmetic_is_counted():
    """`Brent` is named ``brent``, at version 2, and its arithmetic is flop-counted."""
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=1e-3, max_fevals=20)

    # --- assert -----------------------
    assert (Brent.name, Brent.version) == ("brent", 2)
    assert result.flop_counts.total_count() > 0


def test_the_stopping_test_counts_both_of_its_comparisons():
    """A solve that stops at its first stopping test counts both comparisons of that test, 8 comparisons in all.

    Both comparisons of the stopping test count because Algol 60 evaluates both operands of a Boolean operator. The 8
    comparisons are:

    - 4 in `Solver.solve`;
    - 1 in the ``max`` of the tolerance ``t``;
    - 1 in the test whether to swap ``b`` and ``c``;
    - 2 in the stopping test.
    """
    # --- act --------------------------
    result = Brent().solve(cubic, 1.0, 2.0, xtol=10.0, max_fevals=20)

    # --- assert -----------------------
    assert result.n_fevals == 2
    assert result.flop_counts.COMP == 8
