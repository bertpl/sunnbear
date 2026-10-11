"""This package tests `Pegasus`.

Published results:

- Dowell and Jarratt (1972), Table 1: reproduced, in ``test_paper.py``: the errors of ``x_2`` to ``x_7``. The errors
  of ``x_8`` and ``x_9`` differ; the paper does not state the precision of its arithmetic.
- Dowell and Jarratt (1972), Problems 1 to 4: not reproduced.
  - Problems 1 to 3 stop once ``|f(x)|`` drops below ``0.5e-17`` or ``0.5e-19``. Near their roots, float64 cannot
    compute ``f(x)`` that accurately, so only an iterate with ``f(x) == 0`` meets that test.
  - Problem 4 computes its function with a Gauss-Hermite rule whose number of points the paper does not state.
- Anderson and Björck (1973), Examples 1 to 7, the Pegasus columns: not reproduced; the test package of
  `AndersonBjorck` gives the reasons.
- Ford (1997), Table 4: not compared; whether it reproduces is not checked.

Reference implementations:

- mpmath's ``Illinois`` with ``method="pegasus"``: compared in ``test_twin.py``.
"""
