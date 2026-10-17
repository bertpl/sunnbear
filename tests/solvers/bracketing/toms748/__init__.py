"""This package tests `TOMS748`.

Published results:

- The test output of the authors' Fortran 77 code (netlib, ``toms/748``): reproduced for ``k = 2``, in
  ``test_paper.py``: the roots of 153 of the 154 problems; the test data states why the root of problem 26
  is not compared.
- Alefeld, Potra and Shi (1995), Table II: reproduced, in ``test_paper.py``: the totals within 1.2 %.
- Alefeld, Potra and Shi (1995), Table III: not reproduced, because the paper does not list the 139 problems behind
  its totals.
- Alefeld, Potra and Shi (1995), Tables IV to VI: reproduced, in ``test_paper.py``: 29 of the 34 evaluation counts
  exactly; the test data states why each of the other 5 deviates.

Third-party published results:

- None.

Reference implementations:

- None: SciPy's ``scipy.optimize.toms748`` keeps no margin from the interval bounds, and uses its own fallbacks and
  stopping rule.
"""
