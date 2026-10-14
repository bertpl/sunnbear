"""This package tests `Pegasus`.

Published results:

- Dowell and Jarratt (1972), Table 1: reproduced, in ``test_paper.py``: the errors of ``x_2`` to ``x_7``. The errors
  of ``x_8`` and ``x_9`` are not compared: in float64, ``x_8``'s error is about 1 % off and ``x_9``'s has the opposite
  sign, and no precision of the arithmetic gives both printed values.
- Dowell and Jarratt (1972), Problems 1 to 4: not compared. Problems 1 to 3 stop once ``|f(x)|`` drops below
  ``0.5e-17`` or ``0.5e-19``, which in float64 only an iterate with ``f(x) == 0`` meets, and Problem 4 cannot be run:
  - Problem 1: the iteration counts for ``N = 2``, 10 and 20 are 13, 12 and 10, against the paper's 13, 13 and 11;
  - Problem 2: the solve reaches ``f(x) == 0`` after 8 iterations for ``K = 3.0``, against the paper's 5, and not
    within 300 evaluations for ``K = 2.5``; the cause of both differences is not known;
  - Problem 3: the solve does not reach ``f(x) == 0`` within 300 evaluations;
  - Problem 4: the paper states no starting values, nor the number of points of the Gauss-Hermite rule that
    computes its function.

Third-party published results:

- Anderson and Björck (1973), Examples 1 to 7, the Pegasus columns: not reproduced; the test package of
  `AndersonBjorck` gives the reasons.
- Ford (1997), Table 4: reproduced, in ``test_third_party.py``: 12 of the 15 iteration counts exactly, and the
  other 3 within 1; the test data states why each of the 3 deviates.

Reference implementations:

- mpmath's ``Illinois`` with ``method="pegasus"``: compared in ``test_twin.py``.
"""
