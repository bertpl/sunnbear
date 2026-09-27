"""The shipped (u, v) tuple set is the data artifact `mc_tuples`; `load_mc_tuples(size)` returns one size of it.

The artifact is 1 CSV file with columns `u` and `v`, one row per tuple, in prefix order: the first
`k` rows are the set of size `k`, for every supported size.
"""

import functools
from collections.abc import Mapping

from sunnbear._core.artifacts import ArtifactDeclaration, ArtifactError, ArtifactStore

from .tuples import MC_TUPLES_SIZES, MCTuples

_CSV_FILE_NAME = "mc_tuples.csv"
_CSV_HEADER = "u,v"


# ==================================================================================================
#  MCTuplesDeclaration
# ==================================================================================================
class MCTuplesDeclaration(ArtifactDeclaration[MCTuples]):
    """`MCTuplesDeclaration` declares the `mc_tuples` artifact: the full tuple set as 1 CSV file."""

    name = "mc_tuples"

    @classmethod
    def to_files(cls, value: MCTuples) -> dict[str, bytes]:
        """Return the CSV file, each value written as the shortest text that reads back to the same float."""
        rows = [_CSV_HEADER] + [f"{float(u)!r},{float(v)!r}" for u, v in zip(value.u, value.v, strict=True)]
        return {_CSV_FILE_NAME: ("\n".join(rows) + "\n").encode()}

    @classmethod
    def from_files(cls, files: Mapping[str, bytes]) -> MCTuples:
        """Rebuild the tuple set from the CSV file.

        Raises:
            ArtifactError: If the CSV file does not start with the header `u,v`.
        """
        header, *rows = files[_CSV_FILE_NAME].decode().splitlines()
        if header != _CSV_HEADER:
            raise ArtifactError(f"{_CSV_FILE_NAME} starts with {header!r}, not {_CSV_HEADER!r}.")
        row_fields = [row.split(",") for row in rows]
        return MCTuples([float(u) for u, _ in row_fields], [float(v) for _, v in row_fields])


# ==================================================================================================
#  load_mc_tuples
# ==================================================================================================
def load_mc_tuples(size: int) -> MCTuples:
    """Return the shipped tuple set of `size` tuples: the first `size` rows of the `mc_tuples` artifact.

    The artifact is read once per process.

    Raises:
        ValueError: If `size` is not one of `MC_TUPLES_SIZES`.
    """
    if size not in MC_TUPLES_SIZES:
        raise ValueError(f"size must be one of {list(MC_TUPLES_SIZES)} (got {size}).")
    return _load_full_set().first(size)


# ==================================================================================================
#  Helpers
# ==================================================================================================
@functools.cache
def _load_full_set() -> MCTuples:
    """Return the full shipped tuple set, read from the `mc_tuples` artifact on the first call."""
    return ArtifactStore.load(MCTuplesDeclaration)
