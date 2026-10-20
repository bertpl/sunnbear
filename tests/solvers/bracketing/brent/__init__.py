"""This package tests `Brent`, in both variants.

The tests of published results reproduce counts of Brent's method, so they run ``"inverse_quadratic"``; no publication
gives counts of ``"hyperbolic"`` that they could reproduce.

The published counts come from runs that stop by the stopping criterion of Brent's procedure ``zero``, so the tests run
`BrentWithPaperStoppingCriterion`, which is `Brent` with that criterion, and pass the procedure's tolerance ``t`` as
``xtol``.

Published results:

- Brent (1971): no numerical results.
- Brent (1973), Table 4.1, the 2 rows on ``x^9``: reproduced, in ``test_paper.py``, with evaluation counts that differ
  from the book's by at most 3; the test data states why. The book ran all 5 rows of the table with its procedure
  ``zero2``, which handles a wider floating-point exponent range than ``zero``; in float64, ``x^9`` does not underflow
  before the solve stops on these 2 rows.
- Brent (1973), Table 4.1, the column of errors of the returned x-values: not compared, because the errors of the
  returned x-values differ from the book's; the cause is not known.
- Brent (1973), Table 4.1, the other 3 rows: not reproduced, because their functions underflow near the root in
  float64, and `Brent` has no counterpart of ``zero2``.
- Brent (1973), Table 4.2: not reproduced, because the book states neither its intervals nor its tolerances, which the
  book's eigenvalue program adjusted.
- Brent (1973), Table 6.1, the column ``n_Z``, the evaluation counts of ``zero`` on 19 intervals with
  ``macheps = 16^-7`` and ``t = 1e-10``: not checked by a test, because `Brent` sets ``macheps`` to 2^-52.

Third-party published results:

- Chandrupatla (1997), Table 2, the column "Brent's": reproduced, in ``test_third_party.py``: all 45 evaluation
  counts, and the number of bisections on each.
- Alefeld, Potra and Shi (1995), Tables IV to VI, the column "BR": reproduced, in ``test_third_party.py``: 16 of the
  17 evaluation counts exactly; the count of the 17th is not checked, and the test data states why.
- Alefeld, Potra and Shi (1995), Table II, the column "BR": reproduced, in ``test_third_party.py``: the totals within
  1 %. The totals of the solve lie below the paper's, for a cause not fully known. Known causes explain part of the
  difference:

  - the paper's relative machine precision, 1.907e-16, not 2^-52;
  - problem ``26[n=1]``, the paper's problem 13: in float64, its function is 0 where ``exp(1 / x^2)`` overflows,
    which ends the solve there, while the paper's section 6 states that its runs found the root 0.

- Alefeld, Potra and Shi (1995), Table III, the column "BR": not reproduced, because the paper does not list the 139
  problems behind its totals.
- Anderson and Björck (1973), Examples 1 to 7, the column "Brent": reproduced, in ``test_third_party.py``: 22 of the
  26 iteration counts exactly, and the other 4 within 1; the test data states why.
- Anderson and Björck (1973), the double-precision totals on p. 263, the column "Brent": not reproduced, cause
  unknown; the paper gives no per-example counts in double precision that could show where the difference arises.

  On Examples 1 to 5, the solve takes 15 to 18 iterations fewer in float64 and in emulated 60-bit arithmetic, the
  double precision of the paper's UNIVAC 1108, and on Examples 6 and 7, 2 fewer in float64.
- Ganchovski et al. (2026), Table 2, the column "Bre": reproduced, in ``test_third_party.py``: 90 of the 92
  evaluation counts exactly, the other 2 within 1, and the roots of all 92 functions; the test data states why the
  2 counts deviate.
- Bus and Dekker (1975), Tables I to IV, the column "B": reproduced, in ``test_third_party.py``: 27 of the 36
  evaluation counts exactly, 5 within 1, 1 within 2 and 1 within 3; the counts of the other 2 are not checked, and the
  test data states why. The article ran its tables on a CDC Cyber 73, whose significand has 48 bits. It states no
  interval for Table II; on ``[-1, 10]``, the interval of Table III, all 12 counts of Table II reproduce.
- Oliveira and Takahashi (2020), Table 1, the column "Matlab": not checked by a test, because its counts are those of
  MATLAB's ``fzero``, a descendant of ``zero``, and the paper does not state which ``t`` its tolerance of 1e-10 gives.
- Gao (2026), Tables 2 and 4, the columns "Brentq": not checked by a test, because their counts are those of SciPy's
  ``brentq``, with a tolerance that the paper does not state.
- Gao (2026), Table 1: not compared. Its third function has random parameters, and on the other 2, neither the solve
  nor ``brentq`` with ``xtol = 1e-10`` reproduces the paper's counts.
- Gao (2026), Table 3: not compared, because its column "Brentq" repeats the totals of the column "BR" of Table II of
  Alefeld, Potra and Shi (1995).
- Gao (2026), the columns "Brenth": not compared with ``"hyperbolic"``, because their counts are those of SciPy's
  ``brenth``, with a tolerance that the paper does not state.

Reference implementations:

- SciPy's ``scipy.optimize.brentq``: compared with ``"inverse_quadratic"`` in ``test_twin.py``, which stops ``brentq``
  by the shared stopping criterion of `Brent`.
- SciPy's ``scipy.optimize.brenth``: compared with ``"hyperbolic"`` in ``test_twin.py``, which stops ``brenth`` by the
  shared stopping criterion of `Brent`.
"""
