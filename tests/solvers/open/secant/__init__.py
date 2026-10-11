"""Tests of `Secant`.

Published results:

- None: the secant method is a classical method, and Numerical Recipes (2007), section 9.2, gives no numerical
  results.

Reference implementations:

- SciPy's ``scipy.optimize.newton``, without a derivative: compared in ``test_twin.py``, with SciPy's own stopping
  rule.
"""
