"""This package tests `CARF`.

Published results:

- Gao (2026), Table 4: reproduced, in ``test_paper.py``, with the paper's ``eps1 = 1e-15`` and ``eps2 = 1e-12``: 33 of
  the 45 evaluation counts exactly. The table runs on the 45 test problems of Chandrupatla (1997). For the other 12
  counts, the test checks only convergence, and the test data states a reason for each:

  - 8[2e-4, 2] and 9[2e-4, 1], each written as the function's number in Table 4 followed by its interval, differ by
    1: `CARF` takes 11 and 8 evaluations against 12 and 7.

    - The reason in the test data, that a 1-ulp difference in the last step changes the count, gives the paper's 12 on
      8[2e-4, 2], but 9 on 9[2e-4, 1].
    - On 9[2e-4, 1], the paper's 7 follows if the stop test also checks a new x-value that becomes an interval bound:
      in that solve's 4th iteration, such an x-value has ``|f| < eps1``.

  - On the widest intervals of functions 1 to 4, 10 counts differ by 3 to 59:

    - The reason in the test data, that ``h = (f(t) - f(a)) / (f(b) - f(a))`` lies within rounding error of a limit
      that picks the kind of step, fits 8 of the 10, whose solves take steps with such an ``h``.
    - The reason does not fit 1[-1e4, 1e4] and 1[-1e10, 1e10]: there, ``h`` is 0.5 at the first step, and the formula
      of the quadratic's zero decides whether that step is accepted or clipped.
    - Each of the 10 counts changes with the formula of the chord's zero, the quadratic's zero or the power step,
      which the paper does not state for its program; another formula gives the paper's count on 3[-1e6, 1e6],
      4[-1e6, 1e6] and 4[-1e10, 1e10].

- Gao (2026), Table 3: reproduced, in ``test_paper.py``: the totals within 1.5 %, with ``eps1 = 1e-15`` from Table 4,
  because Table 3 states only ``eps2``. With ``eps1 = 0``, the totals lie 3.7 to 8.6 % above the paper's.
- Gao (2026), Table 2: not reproduced, and the cause of the difference is not known:

  - SciPy's ``brentq`` reproduces the table's column "Brentq", counts and errors, at ``xtol = 1e-10``; at that
    tolerance, `CARF` takes 53 and 61 evaluations on the table's x^5 and x^7, against the paper's 37 and 35.
  - No other value of ``eps1`` or formula of a step that was tried reaches the paper's 37 and 35.
  - No reading of the paper's open details that was tried reproduces Table 2 together with Table 4: the closest to
    Table 2, at 39 and 36, matches 8 of Table 4's counts.

- Gao (2026), Table 1: not compared yet. SciPy's ``brentq`` reproduces the table's column "Brentq" for the functions
  ``f`` and ``g``, counts and errors, at ``xtol = 1e-8``, where the text states an error of 1e-10. `CARF` takes 28 and
  38 evaluations against the paper's 29 and 32 at ``xtol = 1e-8``, and 34 and 45 at 1e-10. The third function,
  ``phi``, cannot be compared, because the paper does not publish its random poles and weights.

Third-party published results:

- None.

Reference implementations:

- None: the author's Python program, which the paper mentions, is not public, and no other implementation is known.
"""
