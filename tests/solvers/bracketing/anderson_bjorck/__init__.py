"""This package tests `AndersonBjorck`.

Published results:

- Anderson and Björck (1973), Examples 1 to 7, the column "Alg. A": reproduced, in ``test_paper.py``: 17 of the 26
  iteration counts exactly, 8 within 1, and 1 within 2; the test data states why each of the 9 deviates.

  The test passes the paper's ``delta``, 6e-8, as ``xtol``, so that the steps of delta are the paper's, and stops by the
  shared stopping criterion, not by the paper's, for the reason that the test's docstring gives.
- Anderson and Björck (1973), the double-precision totals on p. 263: not reproduced, cause unknown:

  - at ``xtol = 6e-16``, the paper's ``delta``, `AndersonBjorck` takes 129 iterations on Examples 1 to 5, against the
    paper's 147, and 58 on Examples 6 and 7, against 50;
  - the paper gives no per-example counts in double precision that could show where the difference arises;
  - the table labels its first group "Ex. 1-6", but its single-precision totals are the sums of the counts of
    Examples 1 to 5, so the comparison takes that group as Examples 1 to 5.

Third-party published results:

- Ford (1997), Table 4: reproduced, in ``test_third_party.py``: all 15 iteration counts, including the 4 that
  Ford prints as more than 200.
- Ganchovski et al. (2026), Table 2, the column "AB": not reproduced, because the paper's C# code differs from
  `AndersonBjorck` in 4 ways:

  - the C# code stops when the next chord's zero lies within the code's tolerance of the previous chord's zero, without
    evaluating the function at the new zero, while `AndersonBjorck` stops on the interval width;
  - the C# code starts with no retained bound, so it never scales a function value before its 2nd iteration;
  - the C# code computes the scaling factor as ``1 - f_new / f_previous``, where `AndersonBjorck` computes the ratio of
    2 chord slopes, as its paper does;
  - the C# code takes no step of delta.

- Ganchovski and Traykov (2023), Table 2, the column "AB": not compared, because the paper does not state the stopping
  rule of its runs.

Reference implementations:

- mpmath's ``Illinois`` with ``method="anderson"``: compared in ``test_twin.py``, on every test case of
  `TWIN_TEST_CASES` except those on which both solvers exceed the evaluation budget. mpmath takes no step of delta, so
  the twin takes `AndersonBjorck`'s step of delta in mpmath's place.
"""
