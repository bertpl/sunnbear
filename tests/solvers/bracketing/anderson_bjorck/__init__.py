"""This package tests `AndersonBjorck`.

Published results:

- Anderson and Björck (1973), Examples 1 to 7: not reproduced. The paper ran them in 27-bit arithmetic, and with
  steps of delta, which move a new iterate within ``delta`` of the newest one to exactly ``delta`` from it.
  `AndersonBjorck` leaves these steps out, as its class docstring explains.
- Anderson and Björck (1973), the double-precision totals on p. 263: not reproduced, because those runs take steps
  of delta too.
- Ford (1997), Table 4: not compared; whether it reproduces is not checked.

Reference implementations:

- mpmath's ``Illinois`` with ``method="anderson"``: compared in ``test_twin.py``, on every test case of
  `TWIN_TEST_CASES` except the 2 on which both solvers exceed the evaluation budget.
"""
