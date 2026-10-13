"""This package tests `ITP`.

Published results:

- Oliveira and Takahashi (2020), Table 1, for ``variant="paper_experiments"`` with ``n_slack = 0``: reproduced, in
  ``test_paper.py``: 23 of the 24 iteration counts exactly, and the count for the step function within 1.
- Oliveira and Takahashi (2020), Table 1, for ``variant="paper_pseudocode"``: not reproduced. The table comes from
  the authors' code, which ``"paper_experiments"`` follows; the class docstring of `ITP` explains how the 2 variants
  differ.
- Oliveira and Takahashi (2020), Figures 2 to 5: not compared. They are plots, and Figures 4 and 5 use 1000-bit
  arithmetic.
- ``n_slack = 4``: no published results.

Third-party published results:

- Ganchovski et al. (2026), Table 2, the column "ITP": not reproduced. The paper's C# code runs ITP with
  ``n_slack = 1`` and the projection radius of the ``"paper_pseudocode"`` variant, which `ITP` supports, but the C#
  code stops at an interval width of about 1e-14 while it derives ``n_max`` from a larger tolerance; `ITP` derives
  both the stopping width and ``n_max`` from its single ``xtol``.

Reference implementations:

- None: neither SciPy nor mpmath implements ITP.
"""
