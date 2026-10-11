"""Tests of `RegulaFalsi`.

Published results:

- Ford (1997) and Numerical Recipes (2007), section 9.2: no numerical results for the unmodified method.
- Dowell and Jarratt (1971), Tables 2 to 7, the Regula Falsi columns: not reproduced. The tables stop on
  ``|f(x)| < 0.5e-19``, which float64 reaches near most of their roots only through an exact zero, so the iteration
  counts cannot be compared.

Reference implementations:

- None: no Python package implements the unmodified method.
"""
