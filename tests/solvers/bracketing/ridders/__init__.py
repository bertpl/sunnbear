"""This package tests `Ridders`.

Published results:

- Ridders (1979), the example of section I: reproduced, in ``test_paper.py``: the first iteration.
- Ridders (1979), Section III: reproduced, in ``test_paper.py``: every printed iterate of the 5 runs, by every
  variant.

Third-party published results:

- Ganchovski et al. (2026), Table 2, the column "Rid", for the ``"commons_math"`` variant: reproduced, in
  ``test_third_party.py``:

  - 85 of the 92 evaluation counts exactly; the test data states why the other 7 deviate;
  - the roots of all 92 functions, 4 of them within a wider tolerance; the test data states why each needs it.
- Ganchovski et al. (2026), Table 2, for the ``"scipy"`` and ``"bracketing_solver"`` variants: not reproduced, because
  their stopping rules differ from that of the paper's C# code, which is the rule of ``"commons_math"``.

Reference implementations:

- SciPy's ``scipy.optimize.ridder``: compared in ``test_twin.py``, for every variant.
- Apache Commons Math's ``RiddersSolver``, whose stopping criterion the ``"commons_math"`` variant follows: not
  compared, because Apache Commons Math is a Java library.
"""
