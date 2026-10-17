"""This package tests `SteffenBrent`.

Published results:

- Steffen et al. (2025), case studies 1 and 2: reproduced, in ``test_paper.py``: the roots of both, and the evaluation
  counts of the 6 iterations that the paper's figures show, exactly in case 1 and to within 1 in case 2, where the
  solve evaluates 1 more midpoint; the test data states why.

  The paper's runs stop by the criterion of its Algorithm 2, so the tests run a test-only subclass of `SteffenBrent`
  with that stopping criterion and return value. The paper prints 1 tolerance, 1e-10, and only for case 2; the tests use
  it as both of Algorithm 2's tolerances, in both cases.
- Steffen et al. (2025), the modified Brent method's panels of Figures 3, 4, 6 and 7: reproduced to the precision of
  reading the plots, in ``test_paper.py``, with the same subclass, except the 6th width ratio of case 2, which the
  extra midpoint changes.
- Steffen et al. (2025), Table 1: not compared: it gives mean execution times.

Third-party published results:

- None.

Reference implementations:

- None: rateslib's ``_brent``, the only one known, evaluates Algorithm 2's midpoint ``(a + b) / 2``, where
  `SteffenBrent` evaluates ``(a + s) / 2``, and its license allows only non-commercial use.
"""
