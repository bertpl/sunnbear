"""This package tests `Brent`.

Published results:

- Brent (1971): no numerical results.
- Brent (1973), Table 4.1: the 2 rows on ``x^9`` reproduced, in ``test_paper.py``, with evaluation counts within 3
  and 2 of the book's. The other 3 rows are not reproduced: their functions underflow near the root, and the book
  solves them with its procedure ``zero2``, which handles a wider floating-point exponent range than ``zero``.
- Brent (1973), Table 4.2: not reproduced, because the book does not state its intervals.

Reference implementations:

- SciPy's ``scipy.optimize.brentq``: compared in ``test_twin.py``.
"""
