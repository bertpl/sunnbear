"""Distillation, the seventh pipeline stage, selects the benchmark and calibration suites from the Core.

`DistillationStage`, in `stage`, selects each `SuiteFamily`'s suites from the Core.
"""

from .stage import SMALLEST_SUITE_SIZE, DistillationStage
