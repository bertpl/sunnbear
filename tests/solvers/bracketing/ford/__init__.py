"""This package tests `Ford`.

Published results:

- Ford (1997), Table 4, the columns "Method 1", "Method 3" and "Method 4": reproduced, in ``test_paper.py``: 38 of the
  45 iteration counts exactly, 6 within 1, and 1 not reproduced; the test data states why each of the 7 deviates. The
  test solves at ``xtol = 0`` and counts the iterations until the article's stopping rule stops.

  The count of Method 4 on ``3[350,850]`` is not reproduced, cause unknown: `Ford` takes 13 iterations, against Ford's
  19, and the count stays 13 in arithmetic of 53 to 113 bits, while Methods 1 and 3 reproduce their counts on the same
  problem.
- Ford (1997), Table 4, the column "Method 2": not compared, because `Ford` does not implement Method 2.
- Ford (1997), the asymptotic patterns of steps and the orders of convergence that its analysis derives: not compared,
  because they describe the steps near a simple root in exact arithmetic, not a run that the article reports.

Third-party published results:

- None.

Reference implementations:

- None: no Python package implements the methods.
"""
