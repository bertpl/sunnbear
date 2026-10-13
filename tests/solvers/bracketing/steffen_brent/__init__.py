"""This package tests `SteffenBrent`.

Published results:

- Steffen et al. (2025), case studies 1 and 2: reproduced, in ``test_paper.py``: the roots of both, the iteration
  count of case 2, and that of case 1 within 1, because the paper's run stops on ``|f(b)|``.
- Steffen et al. (2025), the modified Brent method's panels of Figures 3, 4, 6 and 7: reproduced to the precision of
  reading the plots, in ``test_paper.py``. Only the midpoint that `SteffenBrent` declares in its class docstring
  reproduces them.

Third-party published results:

- None.

Reference implementations:

- None: rateslib's ``_brent``, the only one known, is licensed for non-commercial use only.
"""
