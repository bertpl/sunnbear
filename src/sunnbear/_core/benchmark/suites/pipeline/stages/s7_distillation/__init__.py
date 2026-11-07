"""Distillation, the seventh pipeline stage, selects the a-series and the b-series of benchmark suites from the Core.

`DistillationStage`, in `stage`, selects both series' suites from the Core.
"""

from .stage import SMALLEST_SUITE_SIZE, DistillationStage
