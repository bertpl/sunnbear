"""This module defines the exception raised when a (u, v) tuple set cannot be constructed."""

from sunnbear._core.exceptions import SunnbearError


class UvTuplesConstructionError(SunnbearError):
    """Raised when `generate_uv_tuples` selects a set that breaks its span or inclusion constraints."""
