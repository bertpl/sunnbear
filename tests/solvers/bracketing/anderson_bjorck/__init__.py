"""This package tests `AndersonBjorck`.

Published results:

- Anderson and Björck (1973), Examples 1 to 7, the 26 iteration counts of the column "Alg. A": not checked by a test;
  the record of `AndersonBjorck` lists them as TBD. The paper ran them in 27-bit arithmetic, and with steps of delta:
  a new iterate that lies within ``delta``, the paper's tolerance, of the newest iterate is moved to exactly ``delta``
  from it. `AndersonBjorck` leaves these steps out. At ``xtol = 6e-8``, the paper's ``delta``:

  - 10 counts match, 11 differ by 1, and 5 differ by 2 or 3: ``2[n=1]`` (6 against the paper's 4), ``4[n=5]`` (8
    against 6), ``4[n=15]`` (12 against 9), ``6[n=15]`` (9 against 7) and ``7[n=5]`` (3 against 5);
  - a port of the paper's ALGOL procedure that takes the steps of delta, in emulated 27-bit arithmetic that rounds to
    nearest, brings those 5 counts to within 1 of the paper's, 4 of them exactly, but does not end on 8 of the other
    21 examples.

- Anderson and Björck (1973), the double-precision totals on p. 263: not reproduced, cause unknown. At
  ``xtol = 6e-16``, the paper's ``delta``, `AndersonBjorck` takes 133 iterations on Examples 1 to 5, against the
  paper's 147, and 60 on Examples 6 and 7, against 50. The steps of delta cannot be checked as the cause: a port of the
  paper's ALGOL procedure that takes them does not end on 10 of the 26 examples in emulated 60-bit arithmetic, the
  double precision of the paper's UNIVAC 1108, and the paper gives no per-example counts in double precision. The
  table labels its first group "Ex. 1-6", but its single-precision totals are the sums of the iteration counts of
  Examples 1 to 5.

Third-party published results:

- Ford (1997), Table 4: reproduced, in ``test_third_party.py``: all 15 iteration counts, including the 4 that
  Ford prints as more than 200.
- Ganchovski et al. (2026), Table 2, the column "AB": not reproduced, because the paper's C# code, which produced the
  column, differs from `AndersonBjorck` in 3 ways:

  - the C# code stops when the next chord's zero lies within the code's tolerance of the previous chord's zero, without
    evaluating the function at the new zero, while `AndersonBjorck` stops on the interval width;
  - the C# code starts with no retained bound, so it never scales a function value before its 2nd iteration;
  - the C# code computes the chord's zero and the scaling factor in a different algebraic form from `AndersonBjorck`.

  A port of the C# code reproduces all 92 evaluation counts and roots of the column. With the C# code's stopping rule
  applied to the history of its solves, `AndersonBjorck` matches 71 of the 92 counts and lies within 1 of 87; 2 of
  the 71 are rows on which both exceed the C# code's limit of 200 iterations.
- Ganchovski and Traykov (2023), Table 2, the column "AB": not compared, because the paper does not state the stopping
  rule of its runs.

Reference implementations:

- mpmath's ``Illinois`` with ``method="anderson"``: compared in ``test_twin.py``, on every test case of
  `TWIN_TEST_CASES` except those on which both solvers exceed the evaluation budget.
"""
