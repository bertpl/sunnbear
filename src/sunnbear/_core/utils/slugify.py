"""This module turns a display name into a lowercase identifier that can serve as a Python module name."""

import re
import unicodedata


def slugify(name: str) -> str:
    """Return `name` as a lowercase identifier, e.g. "Standard function families" as ``standard_function_families``.

    The conversion runs in 3 steps:

    - accented letters lose their accent, and other non-ASCII characters are dropped
    - each run of characters outside a-z and 0-9 becomes 1 underscore
    - leading and trailing underscores are removed

    The result is a valid Python module name as long as it does not start with a digit.
    """
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")
