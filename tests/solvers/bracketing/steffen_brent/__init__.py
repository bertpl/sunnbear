"""This package tests `SteffenBrent`.

Published results:

- Steffen et al. (2025), case studies 1 and 2: reproduced, in ``test_paper.py``: the roots of both, the 6 iterations
  in the paper's figures for case 2, and those for case 1 to within 1 iteration. The paper states no tolerance for
  case 1. `SteffenBrent` passes 0 as the paper's tolerance ``tol2`` on ``|f(b)|``, and ends case 1 at an exact zero in
  a 7th iteration; with any ``tol2`` from 1.6e-15 to 3.2e-10, `SteffenBrent` stops case 1 after the paper's 6
  iterations.
- Steffen et al. (2025), the modified Brent method's panels of Figures 3, 4, 6 and 7: reproduced to the precision of
  reading the plots, in ``test_paper.py``.
- Steffen et al. (2025), Table 1: not compared: it gives mean execution times.

Third-party published results:

- None.

Reference implementations:

- None: rateslib's ``_brent``, the only one known, implements the paper's Algorithm 2 with its midpoint
  ``(a + b) / 2``, where `SteffenBrent` evaluates ``(a + s) / 2``, so the 2 implementations evaluate different
  x-values from the first midpoint on; and rateslib's license allows only non-commercial use.
"""
