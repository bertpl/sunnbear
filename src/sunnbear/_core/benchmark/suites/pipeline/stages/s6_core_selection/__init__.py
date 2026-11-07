"""Core selection, the sixth stage of the benchmark suite pipeline, selects the Core among the candidates.

The Core is the basis of every benchmark suite: a set of candidates, of a size from `CORE_SIZES`, that holds each
difficulty tier in a fixed share when the candidates allow it. `CoreSelectionStage`, in `stage`, assigns each candidate
its tier, chooses the Core's size and quotas, and selects the Core by max-div.
"""

from .stage import CORE_SIZES, CoreSelectionStage
