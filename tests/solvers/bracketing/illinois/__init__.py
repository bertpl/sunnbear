"""This package tests `Illinois`.

Published results:

- Dowell and Jarratt (1971), Table 1: reproduced, in ``test_paper.py``: the errors of ``x_2`` to ``x_9``. The error
  of ``x_10`` lies below the spacing of float64 values near the root.
- Dowell and Jarratt (1971), Tables 2 to 7: not reproduced. The tables stop once ``|f(x)| < 0.5e-19``. Near most
  of their roots, float64 cannot compute ``f(x)`` that accurately, so only an iterate with ``f(x) == 0`` meets that
  test.
- Dowell and Jarratt (1972), Problems 1 to 4, and Anderson and Björck (1973), Examples 1 to 7, the Illinois
  columns: not reproduced; the test packages of `Pegasus` and `AndersonBjorck` give the reasons.
- Ford (1997), Table 4: not compared; whether it reproduces is not checked.

Reference implementations:

- mpmath's ``Illinois`` with ``method="illinois"``: compared in ``test_twin.py``.
"""
