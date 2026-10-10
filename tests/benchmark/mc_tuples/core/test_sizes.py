"""`MCTuplesSize` lists the sizes of the shipped set and the sizes up to a given one, and splits each size into the size
below and its new tuples."""

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


@pytest.mark.parametrize(
    "size, n_required, n_new",
    [
        (MCTuplesSize.SIZE_32, 0, 32),  # the smallest size has no size below
        (MCTuplesSize.SIZE_64, 32, 32),
        (MCTuplesSize.SIZE_1024, 512, 512),
    ],
)
def test_n_required_and_n_new_split_a_size_into_the_size_below_and_its_new_tuples(size, n_required, n_new):
    """A size takes `n_required` tuples from the size below and adds `n_new` new ones."""
    # --- act / assert -----------------
    assert (size.n_required, size.n_new) == (n_required, n_new)
