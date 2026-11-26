"""Suite selection, the sixth and last stage of the benchmark suite pipeline, selects every benchmark suite.

`SuiteSelectionStage`, in `stage`, selects the largest suite of the a-series and of the b-series from all candidates,
then selects each smaller suite of a series, of half the size, from the series' next larger suite, down to
`SMALLEST_SUITE_SIZE`.
"""

from .stage import MAX_SUITE_SIZE, SMALLEST_SUITE_SIZE, SuiteSelectionStage
