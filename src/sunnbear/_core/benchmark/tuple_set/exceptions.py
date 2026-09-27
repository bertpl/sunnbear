"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class UvTuplesConstructionError(SunnbearError):
    """`UvTuplesConstructionError` is raised when `generate_uv_tuples` selects repeated tuples, or tuples that
    break a span or inclusion constraint.
    """
