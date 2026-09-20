"""The base class of every sunnbear-raised exception.

Each layer defines the exceptions it raises next to the code that raises them,
all deriving from `SunnbearError`, so callers can catch the package's failures
with one handler while still discriminating on the specific subclass. The
`sunnbear.exceptions` façade re-exports the whole taxonomy.
"""


class SunnbearError(Exception):
    """Base class for all sunnbear-raised exceptions."""
