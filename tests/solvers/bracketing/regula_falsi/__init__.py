"""This package tests `RegulaFalsi`.

Published results:

- Ford (1997) and Numerical Recipes (2007), section 9.2: no numerical results for the unmodified method.
- Dowell and Jarratt (1971), Tables 2 to 7, the Regula Falsi columns: not reproduced. The tables stop once
  ``|f(x)| < 0.5e-19``. Near most of their roots, float64 cannot compute ``f(x)`` that accurately, so only an
  iterate with ``f(x) == 0`` meets that test, and the iteration counts cannot be compared.

Reference implementations:

- None: no Python package implements the unmodified method.
"""
