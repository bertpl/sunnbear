"""This package tests `Ridders`.

Published results:

- Ridders (1979), the example of section I: reproduced, in ``test_paper.py``: the first iteration.
- Ridders (1979), Section III: reproduced, in ``test_paper.py``: every printed iterate of the 5 runs, by every
  variant. The number of iterates in each run is not compared, because the paper states no stopping rule.

Third-party published results:

- Ganchovski et al. (2026), Table 2, the column "Rid", for the ``"scipy"`` variant, the core variant (role
  ``SolverRole.BUILTIN_CORE``): reproduced, in ``test_third_party.py``:

  - 74 of the 92 evaluation counts exactly; the test data states why the other 18 deviate, 11 of them because the
    paper's C# code uses the stopping rule of the ``"commons_math"`` variant;
  - the roots of 90 of the 92 functions, to within twice the paper's tolerance, or a wider tolerance where the test
    data states why; on f72 and f73, it returns the true root, because the paper's root there is not a
    root of the function.
- Ganchovski et al. (2026), Table 2, the column "Rid", for the ``"commons_math"`` variant, whose stopping rule is that
  of the paper's C# code: reproduced, in ``test_third_party.py``:

  - 85 of the 92 evaluation counts exactly; the test data states why the other 7 deviate;
  - the roots of all 92 functions, 4 of them within a wider tolerance; the test data states why each needs it.
- Ganchovski et al. (2026), Table 2, for the ``"bracketing_solver"`` variant: not reproduced, because its stopping
  rule differs from that of the paper's C# code.
- Oliveira and Takahashi (2020), Table 1, the column "Ridders'": not compared by a test. The table's runs stop by
  the rule of `BracketingSolver`, the rule of the ``"bracketing_solver"`` variant, with ``xtol = 1e-10`` on
  ``[-1, 1]``, and its counts leave out the 2 evaluations at the interval bounds. Counted that way, the
  ``"bracketing_solver"`` variant matches 19 of the 24 counts, and differs on the other 5:

  - "Trigonometric 1": 12, against the table's 10;
  - "Polynomial 1": 26, against 14;
  - "Normal CDF": 18, against 16;
  - "Circles": 35, against 36;
  - "Noisy Line": 22, against 24.
- Ganchovski and Traykov (2023), Table 2, the column "Rid": not compared, because the paper does not state the stopping
  rule of its Ridders runs.
- Gorgey et al. (2025), Tables 2 to 7, the rows "Ridders'": not compared, because the paper does not fix how its runs
  were set up:

  - it states 2 different stopping tests for its runs: a test on the interval width in its pseudocode, and a test on
    ``|f|`` in its Table 1;
  - it states 2 different intervals for each of its Equations 1 and 3.

Reference implementations:

- SciPy's ``scipy.optimize.ridder``: compared in ``test_twin.py``, for every variant.
- Apache Commons Math's ``RiddersSolver``, whose stopping rule the ``"commons_math"`` variant follows: not
  compared, because Apache Commons Math is a Java library.
"""
