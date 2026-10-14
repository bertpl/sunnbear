"""This package tests `ITP`.

Published results:

- Oliveira and Takahashi (2020), Table 1, for ``variant="paper_experiments"`` with ``n_slack = 0``: reproduced, in
  ``test_paper.py``: 23 of the 24 iteration counts exactly, and the count for the step function within 1.

  - On the step function, `ITP` takes 35 iterations, against the table's 34: in float64, rounding in the interval
    bounds leaves the interval slightly wider than ``2 * xtol`` after iteration 34, and a line-by-line port of the
    authors' MATLAB code takes 35 too.
  - The same algorithm in exact rational arithmetic takes 34; what gave the published run 34 is not known.

- Oliveira and Takahashi (2020), Table 1, the rows "Global Average" and "Global Worst Case", and Table 2, which gives
  the mode, median and mean of Table 1's counts per group of 12 functions: not checked by a test; the record of `ITP`
  lists them as TBD. The counts of ``"paper_experiments"`` with ``n_slack = 0`` reproduce every value of these rows
  and of Table 2's column "ITP", except the worst case, 35 against 34.
- Oliveira and Takahashi (2020), Table 1, for ``variant="paper_pseudocode"``: not reproduced. The table comes from
  the authors' code, which ``"paper_experiments"`` follows; the class docstring of `ITP` explains how the 2 variants
  differ. With ``"paper_pseudocode"``, 17 of the 24 counts match, and the other 7 take 1 to 19 iterations more.
- Oliveira and Takahashi (2020), Figures 2 to 5: not compared. They are plots, and Figures 4 and 5 use 1000-bit
  arithmetic.
- ``n_slack = 4``: no published results.

Third-party published results:

- Ganchovski et al. (2026), Table 2, the column "ITP": not reproduced. The paper's C# code runs ITP with
  ``n_slack = 1``, and with the projection radius of the paper's pseudocode clamped at 0, without the margin of
  ``"paper_experiments"``; no config of `ITP` runs these settings. The C# code also stops at an interval width of
  about 1e-14 while it derives ``n_max`` from a larger tolerance, where `ITP` derives both the stopping width and
  ``n_max`` from its single ``xtol``.
- Ganchovski and Traykov (2023), Table 2, the column "ITP": not compared, because the paper states neither the code
  nor the settings of its ITP runs.

Reference implementations:

- None: neither SciPy nor mpmath implements ITP, and the C# ITP of Ganchovski et al. (2026) cannot run in the test
  suite.
"""
