"""This package tests `SteffenBrent`.

Published results:

- Steffen et al. (2025), case studies 1 and 2: reproduced, in ``test_paper.py``: the roots of both, and the iteration
  counts of both to within 1 iteration:

  - in case 1, the paper's run stops once ``|f(b)|`` is small enough, while `SteffenBrent` stops on the width of the
    interval;
  - in case 2, `chord_zero` puts the last secant step 1 ulp from the x-value of the paper's equation 4, on a float
    where rounding gives ``f`` the sign opposite to its sign at that x-value, so the solve evaluates 1 more midpoint.
- Steffen et al. (2025), the modified Brent method's panels of Figures 3, 4, 6 and 7: reproduced to the precision of
  reading the plots, in ``test_paper.py``, except the 6th width ratio of case 2, which changes with the extra
  iteration.

Third-party published results:

- None.

Reference implementations:

- None: rateslib's ``_brent``, the only one known, is licensed for non-commercial use only.
"""
