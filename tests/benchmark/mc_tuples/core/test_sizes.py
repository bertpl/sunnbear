"""`MCTuplesSize` lists the sizes of the shipped set, and the sizes up to a given one."""

import pytest

from sunnbear._core.benchmark.mc_tuples import MCTuplesSize


@pytest.mark.parametrize(
    "max_size, sizes",
    [
        (MCTuplesSize.SIZE_32, (32,)),
        (64, (32, 64)),  # a plain int is accepted
        (MCTuplesSize.SIZE_1024, tuple(MCTuplesSize)),
    ],
)
def test_up_to_lists_every_size_up_to_max_size(max_size, sizes):
    """`up_to` returns every size up to `max_size`, the smallest first, for a member or a plain int."""
    # --- act / assert -----------------
    assert MCTuplesSize.up_to(max_size) == sizes


def test_up_to_rejects_a_size_outside_the_set():
    """`up_to` raises a `ValueError` naming the sizes for an int that is not 1 of them."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="must be one of"):
        MCTuplesSize.up_to(100)
