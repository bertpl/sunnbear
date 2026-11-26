"""Suite selection, the sixth and last stage of the benchmark suite pipeline, selects every benchmark suite.

`SuiteSelectionStage`, in `stage`, selects the largest suite of the a-series and of the b-series from all candidates,
then halves each series down to `SMALLEST_SUITE_SIZE`.
"""

from .stage import MAX_SUITE_SIZE, SMALLEST_SUITE_SIZE, SuiteSelectionStage
