"""This package tests `Brent`.

Published results:

- Brent (1971): no numerical results.
- Brent (1973), Table 4.1, the 2 rows on ``x^9``: reproduced, in ``test_paper.py``, with evaluation counts that
  differ from the book's by at most 3. The book ran all 5 rows of the table with its procedure ``zero2``, which
  handles a wider floating-point exponent range than its procedure ``zero``; in float64, ``x^9`` does not underflow
  before `Brent` stops on these 2 rows, so `Brent`, which follows ``zero``, can run them. Per row:

  - on ``[-1, 4]``: 191 evaluations on macOS and 186 on Linux on ARM, against the book's 189. The count depends on how
    ``x^9`` is computed: on macOS, 4 ways of computing ``x^9`` give 187 to 192 evaluations in float64, and 3 ways give
    177 to 189 in an emulation of the truncating hexadecimal arithmetic of the book's IBM 360.
  - on ``[-1, 1.1]``: 78 evaluations on macOS against the book's 81, with each of the 4 ways of computing ``x^9``, and
    also in that emulation; the cause is not known. The test data names the IBM 360's truncating arithmetic and the
    platform's ``pow`` as the cause, which neither the emulation nor the 4 ways of computing ``x^9`` confirm.

- Brent (1973), Table 4.1, the column of errors of the returned x-values: not compared, because the errors of the
  x-values that `Brent` returns, ``-1.7e-10`` on ``[-1, 1.1]`` and ``1.3e-21`` on ``[-1, 4]``, differ from the book's
  ``4.99e-10`` and ``4.92e-21``; the cause is not known.
- Brent (1973), Table 4.1, the other 3 rows: not reproduced, because their functions underflow near the root in
  float64, and `Brent` has no counterpart of ``zero2``.
- Brent (1973), Table 4.2: not reproduced, because the book states neither its intervals nor its tolerances, which the
  book's eigenvalue program adjusted.
- Brent (1973), Table 6.1, the column ``n_Z``, the evaluation counts of ``zero`` on 19 intervals with
  ``macheps = 16^-7`` and ``t = 1e-10``: not checked by a test. A run of `Brent` with `FLOAT64_EPS` set to
  ``16^-7`` reproduces all 19 counts; `Brent` as it is, with ``2^-52``, matches 2 of them, and takes 1 or 2 evaluations
  more on the other 17.

Third-party published results:

- Chandrupatla (1997), Table 2, the column "Brent's": reproduced, in ``test_third_party.py``: all 45 evaluation
  counts, and the number of bisections on each.
- Alefeld, Potra and Shi (1995), Tables IV to VI, the column "BR": reproduced, in ``test_third_party.py``: 16 of the
  17 evaluation counts exactly; the count of the 17th is not checked, and the test data states why.
- Alefeld, Potra and Shi (1995), Table II, the column "BR": reproduced, in ``test_third_party.py``: the totals within
  1 %. `Brent`'s totals, 2797, 2900, 2964 and 2980, lie 5 to 28 evaluations below the paper's, at most 0.93 %; the
  cause is not fully known:

  - with the paper's relative machine precision, 1.907e-16, in place of ``2^-52``, only the total at ``t = 0``
    changes, by 2;
  - with problem ``26[n=1]``, the paper's problem 13, coded so that it stays nonzero where ``exp(1 / x^2)``
    overflows, the totals lie 0 to 23 evaluations below the paper's. The paper's section 6 states that its runs found
    the root 0 of this problem; in float64, a solve reaches 0 only if the function stays nonzero where
    ``exp(1 / x^2)`` overflows, because a function value of 0 there ends the solve at that point.

- Alefeld, Potra and Shi (1995), Table III, the column "BR": not reproduced, because the paper does not list the 139
  problems behind its totals.
- Anderson and Björck (1973), Examples 1 to 7, the column "Brent": reproduced, in ``test_third_party.py``: 22 of the
  26 iteration counts exactly, and the other 4 within 1; the test data states why.
- Anderson and Björck (1973), the double-precision totals on p. 263, the column "Brent": not reproduced, cause
  unknown. On Examples 1 to 5, `Brent` takes 15 to 18 iterations fewer in float64 and in emulated 60-bit arithmetic,
  the double precision of the paper's UNIVAC 1108, and on Examples 6 and 7, 2 fewer in float64; the paper gives no
  per-example counts in double precision that could show where the difference arises.
- Ganchovski et al. (2026), Table 2, the column "Bre": reproduced, in ``test_third_party.py``: 90 of the 92
  evaluation counts exactly, the other 2 within 1, and the roots of all 92 functions; the test data states why the
  2 counts deviate.
- Oliveira and Takahashi (2020), Table 1, the column "Matlab": not checked by a test. Its counts are those of MATLAB's
  ``fzero``, which is based on a Fortran version of ``zero``:

  - the paper runs ``fzero`` on ``[-1, 1]`` with an absolute tolerance of 1e-10;
  - like the table's other columns, the counts leave out the 2 evaluations at the interval bounds;
  - with ``t = 2e-10``, twice the paper's tolerance, because the stopping rule of ``fzero`` uses twice the given
    tolerance on ``[-1, 1]``, 23 of the 24 counts match those of `Brent`, which takes 1 evaluation fewer on
    ``pi^x - e``.

- Gao (2026), Tables 2 and 4, the columns "Brentq": not checked by a test. Their counts are those of SciPy's
  ``brentq``, with a tolerance that the paper does not state. With ``xtol = 1e-10`` for ``brentq`` and the same
  tolerance, ``t = 5e-11``, for `Brent`:

  - ``brentq`` reproduces both counts of Table 2 and 42 of the 45 of Table 4;
  - `Brent` matches both counts of Table 2 and 35 of Table 4;
  - on ``x^19``, `Brent` takes 10 to 13 evaluations more than ``brentq``, which computes the inverse quadratic step
    from divided differences: the product in that step's denominator underflows to 0 there, so ``brentq`` bisects
    where `Brent` interpolates.

- Gao (2026), Table 1: not compared. Its third function has random parameters, and on the other 2, `Brent` and
  ``brentq`` with ``xtol = 1e-10`` each take 29 evaluations on the first and 35 on the second, against the paper's 25
  and 29.
- Gao (2026), Table 3: not compared, because its column "Brentq" repeats the totals of the column "BR" of Table II of
  Alefeld, Potra and Shi (1995).
- Gao (2026), the columns "Brenth": not compared, because SciPy's ``brenth`` replaces inverse quadratic interpolation
  by hyperbolic extrapolation, a different method.

Reference implementations:

- SciPy's ``scipy.optimize.brentq``: compared in ``test_twin.py``.
"""
