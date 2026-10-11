"""Tests of `Illinois`.

Published results:

- Dowell and Jarratt (1971), Table 1: reproduced, in ``test_paper.py``: the errors of ``x_2`` to ``x_9``. The error
  of ``x_10`` lies below the spacing of float64 values near the root.
- Dowell and Jarratt (1971), Tables 2 to 7: not reproduced. The tables stop on ``|f(x)| < 0.5e-19``, which float64
  reaches near most of their roots only through an exact zero: on 13 of the 24 rows, no iterate reaches it.
- Dowell and Jarratt (1972), Problems 1 to 4, and Anderson and Björck (1973), Examples 1 to 7, the Illinois
  columns: not reproduced, for the reasons that the test packages of `Pegasus` and `AndersonBjorck` give.
- Ford (1997), Table 4: not compared yet.

Reference implementations:

- mpmath's ``Illinois`` with ``method="illinois"``: compared in ``test_twin.py``.
"""
