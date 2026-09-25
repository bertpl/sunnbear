"""This module defines the exception raised by the data-artifact layer."""

from sunnbear._core.exceptions import SunnbearError


class ArtifactError(SunnbearError):
    """Raised when a data artifact cannot be read or trusted.

    For example, its artifact manifest is malformed, or records a content hash that does not match
    its file entries.
    """
