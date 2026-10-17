"""This package tests `CARF`.

The paper's runs stop by the paper's stopping criterion, with its tolerances ``eps1`` and ``eps2``, so ``test_paper.py``
reproduces its tables with a test-only subclass of `CARF` that stops by that criterion and returns the interior x-value
``t``.

Published results:

- Gao (2026), Table 4: reproduced, in ``test_paper.py``, with ``eps1 = 1e-15`` and ``eps2 = 1e-12``: 33 of the 45
  evaluation counts exactly; for the other 12, the test checks only convergence, and the test data states the reason for
  each.
- Gao (2026), Table 3: reproduced, in ``test_paper.py``: the totals within 1.5 %, with ``eps1 = 1e-15`` from Table 4,
  because Table 3 does not state ``eps1``.
- Gao (2026), Tables 1 and 2: not reproduced, because they state no usable tolerance.

Third-party published results:

- None.

Reference implementations:

- None: the author's program is available only on request.
"""
