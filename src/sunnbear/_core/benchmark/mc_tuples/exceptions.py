"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class MCTuplesConstructionError(SunnbearError):
    """`MCTuplesConstructionError` is raised when `generate_mc_tuples` cannot build a size that meets its constraints.

    - no random starting selection with at most 1 new tuple per fine lane on each axis can be formed;
    - the selection misses a tuple of the size below, or the number of new tuples in a gap between the size below's
      fine lanes differs from the gap's allocation;
    - a fine lane holds 2 tuples, after the selection or after the mean correction.
    """
