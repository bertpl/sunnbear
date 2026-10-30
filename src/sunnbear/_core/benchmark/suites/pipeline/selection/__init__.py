"""This package selects benchmark suites: the most diverse candidates under difficulty quotas.

Core selection and distillation select every suite of the benchmark suite pipeline with the same parts:

- `DifficultyClass`, which buckets a candidate by its empirical difficulty index (EDI), in `difficulty_class`;
- `SuiteComposition`, a suite's difficulty quotas, each a `DifficultyQuota`, in `suite_composition`;
- `select_diverse_suite`, which selects the most diverse suite of a composition from a pool of candidates by max-div,
  in `diverse_selection`.

This package imports nothing from the package `stages` beside it, which uses it.
"""

from .difficulty_class import EDI_GPQ_LEVEL, DifficultyClass
from .diverse_selection import DEFAULT_SELECTION_SEC_PER_CANDIDATE, select_diverse_suite
from .suite_composition import DifficultyQuota, SuiteComposition
