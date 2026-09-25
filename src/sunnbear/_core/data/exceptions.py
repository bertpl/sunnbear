"""This module defines the exception raised by the data-artifact layer."""

from sunnbear._core.exceptions import SunnbearError


class ArtifactError(SunnbearError):
    """Raised when a data artifact cannot be read or trusted, e.g. a malformed or self-contradicting manifest."""
