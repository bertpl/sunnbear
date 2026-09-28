"""This module defines the error raised when a benchmark run folder cannot be used as asked."""

from sunnbear._core.exceptions import SunnbearError


class BenchmarkRunError(SunnbearError):
    """Raised when a benchmark run folder belongs to a different run, or holds no finished run."""
