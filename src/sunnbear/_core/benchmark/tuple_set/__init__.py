"""This package holds the (u, v) tuple set: the class, its construction, and the shipped artifact.

- `UvTuples` holds a set of tuples, maps them onto a test function, and reports their spread as
  `UvTuplesStats`;
- `generate_uv_tuples` constructs a nested set, with settings from `UvTuplesConstructionSettings`;
- `uv_tuples(size)` returns one size of the shipped set, which `UvTuplesDeclaration` declares as
  the data artifact `uv_tuples`.
"""

from .artifact import UvTuplesDeclaration, uv_tuples
from .construction import generate_uv_tuples
from .construction_settings import UvTuplesConstructionSettings
from .exceptions import UvTuplesConstructionError
from .tuples import UV_TUPLES_SIZES, UvTuples, UvTuplesStats
