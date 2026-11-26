"""Suite selection, the sixth stage of the benchmark suite pipeline, selects every benchmark suite.

`SuiteSelectionStage`, in `stage`, selects the largest suite of the a-series and of the b-series from all candidates,
then selects the suite of each smaller size of a series from the series' next larger suite.
"""

from .stage import SuiteSelectionStage
