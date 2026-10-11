"""This package tests `Brent`.

Published results:

- Brent (1971): no numerical results.
- Brent (1973), Table 4.1, the 2 rows on ``x^9``: reproduced, in ``test_paper.py``, with evaluation counts that
  differ from the book's by at most 3; the test data states why.
- Brent (1973), Table 4.1, the other 3 rows: not reproduced. Their functions underflow near the root, and the book
  solves them with its procedure ``zero2``, which handles a wider floating-point exponent range than its procedure
  ``zero``.
- Brent (1973), Table 4.2: not reproduced, because the book does not state its intervals.

Third-party published results:

- None.

Reference implementations:

- SciPy's ``scipy.optimize.brentq``: compared in ``test_twin.py``.
"""
