"""`CRange` is the range within which the benchmark samples a test problem's parameter ``c``."""

from dataclasses import dataclass


# ==================================================================================================
#  CRange
# ==================================================================================================
@dataclass(frozen=True)
class CRange:
    """A `CRange` is a range ``[c_min, c_max]`` of the parameter ``c``, with ``c_min < 0 < c_max``."""

    c_min: float
    c_max: float
