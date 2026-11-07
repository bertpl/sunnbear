"""Distillation, the seventh pipeline stage, selects the a-series and the b-series of benchmark suites from the Core.

`DistillationStage`, in `stage`, splits the Core into the largest suite of each series, then halves each series down to
`SMALLEST_SUITE_SIZE`.
"""

from .stage import SMALLEST_SUITE_SIZE, DistillationStage
