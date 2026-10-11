"""Tests of `SteffenBrent`.

Published results:

- Steffen et al. (2025), case studies 1 and 2: reproduced, in ``test_paper.py``: the roots of both, and the
  evaluation count of case 1.
- Steffen et al. (2025), Figures 3, 4, 6 and 7: not compared. They are plots, and Figure 4's relative interval
  reduction is not defined.

Reference implementations:

- None: rateslib's ``_brent``, the only one known, is licensed for non-commercial use only.
"""
