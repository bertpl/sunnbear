"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class UvTuplesConstructionError(SunnbearError):
    """`UvTuplesConstructionError` is raised when `generate_uv_tuples` selects repeated or constraint-breaking tuples.

    A selection breaks a constraint when a span, or the inclusion of the size below, is not respected.
    """
