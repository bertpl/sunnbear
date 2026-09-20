"""This module defines the base class of every sunnbear-raised exception.

Every sunnbear-raised exception derives from `SunnbearError`, so callers can catch the package's
failures with one handler while still discriminating on the specific subclass.
"""


class SunnbearError(Exception):
    """Base class for all sunnbear-raised exceptions."""
