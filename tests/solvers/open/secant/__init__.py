"""This package tests `Secant`.

Published results:

- None: the secant method is a classical method with no article of its own.

Third-party published results:

- Oliveira and Takahashi (2020), Table 1, the column "Secant": not compared. Its secant method stops once the smaller
  ``|f|`` of its 2 latest x-values is at most 1e-10, and each count is 1 less than the evaluations up to that point.
  Counted that way, `Secant` matches 20 of the 24 counts. 3 differ by 1, and a run that takes the upper bound as the
  newest x-value matches them; on the noisy line, `Secant` needs 73 against the table's 104.
- Atkinson (1989), Table 2.3: not compared: its run starts from ``x0 = 2`` and ``x1 = 1``, while `Secant` on
  ``[1, 2]`` takes 2, the bound with the larger ``|f|``, as the newest x-value, so the 2 runs compute the same ``x2``
  but differ from ``x3`` on.
- Press et al. (2007), section 9.2: no numerical results.

Reference implementations:

- SciPy's ``scipy.optimize.newton``, without a derivative: compared in ``test_twin.py``, with SciPy's own stopping
  rule.
"""
