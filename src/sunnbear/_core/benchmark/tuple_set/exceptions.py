"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class UvTuplesConstructionError(SunnbearError):
    """Raised when `generate_uv_tuples` selects a set that breaks its span or nesting constraints.

    max-div treats constraints as soft and returns its least-violating selection, so a total time
    too short for the solver to meet them ends here, not in a returned set.
    """
