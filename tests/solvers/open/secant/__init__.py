"""This package tests `Secant`.

Published results:

- None: the secant method is a classical method with no article of its own.

Third-party published results:

- Oliveira and Takahashi (2020), Table 1, the column "Secant": not compared. Its secant method stops once the smaller
  ``|f|`` of its 2 latest x-values is at most 1e-10, and each count is the number of evaluations up to that point,
  minus 1. Counted that way, the 24 counts compare with those of `Secant` as follows:
  - 20 match;
  - 3 differ by 1, and a run that takes the upper bound as the newest x-value matches them;
  - 1, on the table's problem ``x + sin(1e6 * x) / 10 + 1e-3``, is 104, where `Secant` needs 79.
- Atkinson (1989), Table 2.3: not compared. Its run takes ``x0 = 2`` as the older x-value and ``x1 = 1`` as the
  newest, while `Secant` on ``[1, 2]`` takes 2, the bound with the larger ``|f|``, as the newest x-value. The 2 runs
  compute the same ``x2`` but differ from ``x3`` on.
- Press et al. (2007), section 9.2: no numerical results.

Reference implementations:

- SciPy's ``scipy.optimize.newton``, without a derivative: compared in ``test_twin.py``, with SciPy's own stopping
  rule, on every test case of `TWIN_TEST_CASES` except those that the twin's docstring excludes.
"""
