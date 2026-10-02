"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class MCTuplesConstructionError(SunnbearError):
    """`MCTuplesConstructionError` is raised when `generate_mc_tuples` selects constraint-breaking tuples.

    A selection breaks a constraint when it does not hold exactly 1 tuple per free band (a band that the size
    below leaves empty), or misses a tuple of the size below.
    """
