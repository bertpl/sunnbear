"""Tests of `AndersonBjorck`.

Published results:

- Anderson and Björck (1973), Examples 1 to 7: not reproduced. The paper ran them in 27-bit arithmetic, with steps
  of delta, which `AndersonBjorck` leaves out because a literal float64 port of them can loop forever.
- Anderson and Björck (1973), the double-precision totals on p. 263: not reproduced. Those runs take steps of delta
  too; `AndersonBjorck` needs 104 iterations against 147 on Examples 1 to 5, and 60 against 50 on Examples 6 and 7.
- Ford (1997), Table 4: not compared yet.

Reference implementations:

- mpmath's ``Illinois`` with ``method="anderson"``: compared in ``test_twin.py``, on every twin case except the 2 on
  which both solvers exceed the evaluation budget.
"""
