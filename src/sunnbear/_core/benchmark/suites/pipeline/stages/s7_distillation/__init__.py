"""Distillation, the seventh stage of the benchmark suite pipeline, distills the benchmark and calibration suites.

From the Core, it selects 2 families of suites, named by `SuiteFamily` in `suite_family`, that share no candidate, each
with 1 suite per power of 2 from `SMALLEST_SUITE_SIZE` up to half the Core. `DistillationStage`, in `stage`, is the
stage.
"""

from .stage import SMALLEST_SUITE_SIZE, SUITE_COMPOSITIONS_REPORT_NAME, SUITE_MEMBERSHIP_SCHEMA, DistillationStage
from .suite_family import SuiteFamily
