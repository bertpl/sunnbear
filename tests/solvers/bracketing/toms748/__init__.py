"""Tests of `TOMS748`.

Published results:

- The authors' test output: reproduced for ``k = 2``, in ``test_paper.py``: the roots of all 154 problems.
- Alefeld, Potra and Shi (1995), Table II: reproduced, in ``test_paper.py``: the totals within 1.1 %.
- Alefeld, Potra and Shi (1995), Table III: not reproduced, because the paper does not list the 139 problems that
  its totals cover.
- Alefeld, Potra and Shi (1995), Tables IV to VI: reproduced, in ``test_paper.py``: 28 of the 34 evaluation counts
  exactly; the test data states why each of the other 6 deviates.

Reference implementations:

- None: SciPy's ``scipy.optimize.toms748`` has no margin from the interval bounds, and its own fallbacks and stopping
  rule.
"""
