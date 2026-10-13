"""This package tests `Illinois`.

Published results:

- Dowell and Jarratt (1971), Table 1: reproduced, in ``test_paper.py``: the errors of ``x_2`` to ``x_9``. The error
  of ``x_10`` is not compared, because it lies below the spacing of float64 values near the root.
- Dowell and Jarratt (1971), Tables 2 to 7: not reproduced. The tables stop once ``|f(x)| < 0.5e-19``. Near most
  of their roots, float64 cannot compute ``f(x)`` that accurately, so only an iterate with ``f(x) == 0`` meets that
  test, and the iteration counts cannot be compared.

Third-party published results:

- Dowell and Jarratt (1972), Problems 1 to 4, the Illinois columns: not reproduced; the test package of `Pegasus`
  gives the reasons.
- Anderson and Björck (1973), Examples 1 to 7, the Illinois columns: not reproduced; the test package of
  `AndersonBjorck` gives the reasons.
- Ford (1997), Table 4: reproduced, in ``test_third_party.py``: 12 of the 15 iteration counts exactly, and the
  other 3 within 1; the test data states why each of the 3 deviates.
- Ganchovski et al. (2026), Table 2, the column "ill": not reproduced, because the paper's C# code differs from
  `Illinois` in 3 ways:

  - the C# code stops when the next chord's zero lies within the code's tolerance of the previous chord's zero, without
    evaluating the function at the new zero, while `Illinois` stops on the interval width;
  - the C# code starts with no retained bound, so it never halves a function value before its 2nd iteration;
  - the C# code computes the chord's zero in a different algebraic form from `Illinois`.

Reference implementations:

- mpmath's ``Illinois`` with ``method="illinois"``: compared in ``test_twin.py``.
"""
