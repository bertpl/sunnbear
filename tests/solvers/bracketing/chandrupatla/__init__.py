"""This package tests `Chandrupatla`.

Published results:

- Chandrupatla (1997), Table 2: reproduced, in ``test_paper.py``: the evaluation counts of all 45 rows, and the
  number of times that the method switches to bisection on each. The paper's runs stop by the criterion of its BASIC
  listing, so the tests run a test-only subclass of `Chandrupatla` with that stopping criterion and return value.
- Chandrupatla (1997), Table 1: not compared: it prints 1 zero per function, and does not say which of the function's
  5 intervals in Table 2 produced it.

Third-party published results:

- None.

Reference implementations:

- SciPy's ``scipy.optimize.elementwise.find_root``: compared in ``test_twin.py``.
"""
