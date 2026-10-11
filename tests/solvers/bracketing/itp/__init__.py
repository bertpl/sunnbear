"""Tests of `ITP`.

Published results:

- Oliveira and Takahashi (2020), Table 1, for ``variant="paper_experiments"`` with ``n_slack = 0``: reproduced, in
  ``test_paper.py``: 23 of the 24 iteration counts exactly, and the step function's within 1.
- Oliveira and Takahashi (2020), Table 1, for ``variant="paper_pseudocode"``: not reproduced. The table comes from
  the authors' code, which ``"paper_experiments"`` follows; its margin keeps the projection radius from going
  negative in floating point, which the pseudocode's radius does, so 7 of the 24 counts differ, by up to 19.
- Oliveira and Takahashi (2020), Figures 2 to 5: not compared. They are plots, and Figures 4 and 5 use 1000-bit
  arithmetic.
- ``n_slack = 4``: no published results.

Reference implementations:

- None: neither SciPy nor mpmath implements ITP.
"""
