"""Distillation, the seventh pipeline stage, selects the benchmark and calibration suites from the Core.

The package holds:

- `SuiteFamily`, which names a family of suites, in `suite_family`;
- `DistillationStage`, which selects each family's suites from the Core, in `stage`.
"""

from .stage import SMALLEST_SUITE_SIZE, SUITE_COMPOSITIONS_REPORT_NAME, SUITE_MEMBERSHIP_SCHEMA, DistillationStage
from .suite_family import SuiteFamily
