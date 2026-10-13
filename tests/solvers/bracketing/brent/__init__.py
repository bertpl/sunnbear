"""This package tests `Brent`.

Published results:

- Brent (1971): no numerical results.
- Brent (1973), Table 4.1, the 2 rows on ``x^9``: reproduced, in ``test_paper.py``, with evaluation counts that
  differ from the book's by at most 3; the test data states why.
- Brent (1973), Table 4.1, the other 3 rows: not reproduced. Their functions underflow near the root, and the book
  solves them with its procedure ``zero2``, which handles a wider floating-point exponent range than its procedure
  ``zero``.
- Brent (1973), Table 4.2: not reproduced, because the book does not state its intervals.

Third-party published results:

- Chandrupatla (1997), Table 2, the column "Brent's": reproduced, in ``test_third_party.py``: all 45 evaluation
  counts, and the number of bisections on each.
- Alefeld, Potra and Shi (1995), Tables IV to VI, the column "BR": reproduced, in ``test_third_party.py``: 16 of the
  17 evaluation counts exactly; the count of the 17th is not checked, and the test data states why.
- Alefeld, Potra and Shi (1995), Table II, the column "BR": reproduced, in ``test_third_party.py``: the totals within
  1 %.
- Alefeld, Potra and Shi (1995), Table III, the column "BR": not reproduced, because the paper does not list the 139
  problems behind its totals.
- Anderson and Björck (1973), Examples 1 to 7, the column "Brent": reproduced, in ``test_third_party.py``: 22 of the
  26 iteration counts exactly, and the other 4 within 1; the test data states why.
- Anderson and Björck (1973), the double-precision totals on p. 263, the column "Brent": not reproduced, cause
  unknown. On Examples 1 to 5, `Brent` takes 15 to 18 iterations fewer in float64 and in emulated 60-bit arithmetic,
  the double precision of the paper's UNIVAC 1108, and the paper gives no per-example counts in double precision that
  could show where the difference arises.
- Ganchovski et al. (2026), Table 2, the column "Bre": reproduced, in ``test_third_party.py``: 90 of the 92
  evaluation counts exactly, the other 2 within 1, and the roots of all 92 functions; the test data states why the
  2 counts deviate.

Reference implementations:

- SciPy's ``scipy.optimize.brentq``: compared in ``test_twin.py``.
"""
