"""`BenchmarkRunError` signals that a benchmark run directory cannot be resumed or read."""

from sunnbear._core.exceptions import SunnbearError


class BenchmarkRunError(SunnbearError):
    """`BenchmarkRunError` is raised when a benchmark run directory cannot be resumed, read or completed."""
