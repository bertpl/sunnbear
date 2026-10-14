"""This package tests `TOMS748`.

Published results:

- Alefeld, Potra and Shi (1995), Tables IV to VI: reproduced, in ``test_paper.py``: the evaluation counts of their 17
  problems at ``tol = 10^-15``, 28 of the 34 counts exactly, and 29 on macOS. The test data states why each of the
  other 6 deviates. The observed deviations:
  - 26[n=1] (problem 26 with ``n = 1``), for ``k = 1`` and 2: 18 and 25 evaluations, against the paper's 28 and 29;
    not compared. In float64, ``x / exp(1 / x^2)`` is 0 for ``|x|`` below about 0.0375, where ``exp`` overflows, and
    the paper's section 6 states that how this function is coded changes the results;
  - 28[n=30], ``k = 2``: 32 against 31;
  - 3[n=1], ``k = 1``: 13 against 15; a change of f by up to 2 ulps moves the count between 12 and 15;
  - 13[n=1], ``k = 1``: 26 against 25;
  - 18[n=1], ``k = 1``: the paper's 11 on macOS, and 10 on Linux on ARM.
- Alefeld, Potra and Shi (1995), Table II: reproduced, in ``test_paper.py``: the total evaluation counts over the 154
  problems at the paper's 4 values of ``tol``, within 1.1 %:
  - the totals lie 0.28 to 0.38 % below the paper's for ``k = 2``, and 0.24 to 1.02 % for ``k = 1``;
  - with problem 26 coded so that `TOMS748` reaches the problem's root 0, as the paper's section 6 reports for its own
    runs, 7 of the 8 totals lie within 0.15 %, and ``k = 1`` at ``tol = 0`` within 0.71 %;
  - using the paper's relative machine precision, 1.9073486328e-16, in place of 2^-52 moves no total by more than 2
    evaluations.
- Alefeld, Potra and Shi (1995), Table III: not reproduced, because the paper does not list the 139 problems behind
  its totals.
- The roots that the test driver of the authors' Fortran 77 code (https://www.netlib.org/toms/748) prints, with
  ``tol = 0``: reproduced for ``k = 2``, in ``test_paper.py``: all 154. The driver's output is published with the code,
  not in the paper. The roots tell ``k = 2`` from ``k = 1`` only on 26[n=1]: ``k = 1``, which the test does not run,
  returns the same roots on the other 153 problems.

Third-party published results:

- None: Gao (2026), Table 3, prints the totals of Algorithm 4.2 from the paper's Table II, not results of a run of its
  own.

Reference implementations:

- None: SciPy's ``scipy.optimize.toms748`` keeps no margin from the interval bounds, and uses its own fallbacks and
  stopping rule. No test runs the authors' Fortran 77 code, which a twin test would have to compile.
"""
