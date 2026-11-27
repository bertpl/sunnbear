"""Suite selection, the sixth stage of the benchmark suite pipeline, selects every benchmark suite.

`SuiteSelectionStage`, in `stage`, selects the largest suite of each built-in series that has enough candidates for
its smallest size, then selects the suite of each smaller size of a series from the series' next larger suite.
`SeriesSelectionSpec`, in `series_selection_spec`, holds the candidates and the quotas of each series' selections.
"""

from .series_selection_spec import SeriesSelectionSpec
from .stage import SuiteSelectionStage
