"""Core selection, the sixth stage of the benchmark suite pipeline, selects the Core among the candidates.

The Core is the basis of every benchmark suite: a set of candidates, of a size from `CORE_SIZES`, that holds each
difficulty class in a fixed share. The package holds:

- `CoreComposition`, the size and difficulty quotas of the largest Core that the candidates can fill, in
  `core_composition`;
- `CoreSelectionStage`, which assigns each candidate its class, chooses the Core's composition and selects the Core by
  max-div, in `stage`.
"""

from .core_composition import CORE_SIZES, MAX_CORE_SIZE, CoreComposition, CoreCompositionWarning
from .stage import CORE_COMPOSITION_REPORT_NAME, DIFFICULTY_CLASS_SCHEMA, CoreSelectionStage
