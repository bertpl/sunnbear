"""This package tests `AndersonBjorck`.

Published results:

- Anderson and Björck (1973), Examples 1 to 7: not reproduced. The paper ran them in 27-bit arithmetic, and with
  steps of delta: a new iterate that lies within ``delta``, the paper's tolerance, of the newest iterate is moved to
  exactly ``delta`` from it. `AndersonBjorck` leaves these steps out, as its class docstring explains.
- Anderson and Björck (1973), the double-precision totals on p. 263: not reproduced, because those runs take steps
  of delta too.

Third-party published results:

- Ford (1997), Table 4: reproduced, in ``test_third_party.py``: all 15 iteration counts, including the 4 that
  Ford prints as more than 200.

Reference implementations:

- mpmath's ``Illinois`` with ``method="anderson"``: compared in ``test_twin.py``, on every test case of
  `TWIN_TEST_CASES` except those on which both solvers exceed the evaluation budget.
"""
