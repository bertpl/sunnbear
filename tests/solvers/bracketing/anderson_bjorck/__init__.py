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
- Ganchovski et al. (2026), Table 2, the column "AB": not reproduced, because the paper's C# code differs from
  `AndersonBjorck` in 3 ways:

  - the C# code stops when the next chord's zero lies within the code's tolerance of the previous chord's zero, without
    evaluating the function at the new zero, while `AndersonBjorck` stops on the interval width;
  - the C# code starts with no retained bound, so it never scales a function value before its 2nd iteration;
  - the C# code computes the chord's zero and the scaling factor in a different algebraic form from `AndersonBjorck`.

Reference implementations:

- mpmath's ``Illinois`` with ``method="anderson"``: compared in ``test_twin.py``, on every test case of
  `TWIN_TEST_CASES` except those on which both solvers exceed the evaluation budget.
"""
