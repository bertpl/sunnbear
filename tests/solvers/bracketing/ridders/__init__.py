"""This package tests `Ridders`.

Published results:

- Ridders (1979), the example of section I: reproduced, in ``test_paper.py``: the first iteration.
- Ridders (1979), Section III: reproduced, in ``test_paper.py``: every printed iterate of the 5 runs, by every
  variant.

Reference implementations:

- SciPy's ``scipy.optimize.ridder``: compared in ``test_twin.py``, for every variant.
- Apache Commons Math's ``RiddersSolver``, whose stopping criterion the ``"commons_math"`` variant follows: not
  compared, because it is a Java library.
"""
