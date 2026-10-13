"""This package tests `Ridders`.

Published results:

- Ridders (1979), the example of section I: reproduced, in ``test_paper.py``: the first iteration.
- Ridders (1979), Section III: reproduced, in ``test_paper.py``: every printed iterate of the 5 runs, by every
  variant.

Third-party published results:

- Ganchovski et al. (2026), Table 2, the column "Rid", for the ``"scipy"`` variant, the core variant (role
  ``SolverRole.BUILTIN_CORE``): reproduced, in ``test_third_party.py``:

  - 74 of the 92 evaluation counts exactly; the test data states why the other 18 deviate, 11 of them because the
    paper's C# code stops by the rule of the ``"commons_math"`` variant;
  - the roots of 90 of the 92 functions, to within twice the paper's tolerance, or a wider tolerance where the test
    data states why; on f72 and f73, the true root, because the paper's root there is no root.
- Ganchovski et al. (2026), Table 2, the column "Rid", for the ``"commons_math"`` variant, whose stopping rule is that
  of the paper's C# code: reproduced, in ``test_third_party.py``:

  - 85 of the 92 evaluation counts exactly; the test data states why the other 7 deviate;
  - the roots of all 92 functions, 4 of them within a wider tolerance; the test data states why each needs it.
- Ganchovski et al. (2026), Table 2, for the ``"bracketing_solver"`` variant: not reproduced, because its stopping
  rule differs from that of the paper's C# code.

Reference implementations:

- SciPy's ``scipy.optimize.ridder``: compared in ``test_twin.py``, for every variant.
- Apache Commons Math's ``RiddersSolver``, whose stopping criterion the ``"commons_math"`` variant follows: not
  compared, because Apache Commons Math is a Java library.
"""
