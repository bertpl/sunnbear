"""`MCTuplesSize` lists the sizes in which the shipped Monte Carlo tuple set comes."""

from enum import IntEnum
from typing import NoReturn


# ==================================================================================================
#  MCTuplesSize
# ==================================================================================================
class MCTuplesSize(IntEnum):
    """`MCTuplesSize` is 1 of the sizes of the shipped Monte Carlo tuple set.

    Each size is a prefix of the next, so a smaller size's tuples are a subset of every larger size's.
    Members compare and compute as plain ints, so `MCTuplesSize(size)` both checks an int size and
    returns it as a member.
    """

    SIZE_32 = 32
    SIZE_64 = 64
    SIZE_128 = 128
    SIZE_256 = 256
    SIZE_512 = 512
    SIZE_1024 = 1024

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        """Raise `ValueError` listing the sizes, for a `value` that is not 1 of them."""
        raise ValueError(f"A Monte Carlo tuple set size must be one of {[int(size) for size in cls]} (got {value!r}).")

    @property
    def size_below(self) -> "MCTuplesSize | None":
        """Return the size that this size includes, half as large; None for the smallest size."""
        return None if self == min(MCTuplesSize) else MCTuplesSize(self // 2)
