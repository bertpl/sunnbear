"""Core selection, the sixth stage of the benchmark suite pipeline, selects the Core among the candidates.

The Core is the basis of every benchmark suite: a set of candidates, of a size from `CORE_SIZES`, that holds each
difficulty class in a fixed share. `CoreSelectionStage`, in `stage`, assigns each candidate its class, chooses the
Core's composition, a `CoreComposition`, and selects the Core by max-div.
"""

from .stage import CoreSelectionStage
