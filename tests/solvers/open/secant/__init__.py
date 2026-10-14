"""This package tests `Secant`.

Published results:

- None: the secant method is a classical method with no paper of its own.

Third-party published results:

- Oliveira and Takahashi (2020), Table 1, the column "Secant": not compared.
- Atkinson (1989), Table 2.3: not compared: its run starts from ``x0 = 2`` and ``x1 = 1``, while `Secant` on
  ``[1, 2]`` takes 2, the bound with the larger ``|f|``, as the newest x-value, so its x-values differ from ``x_3``
  on.
- Press et al. (2007), section 9.2: no numerical results.

Reference implementations:

- SciPy's ``scipy.optimize.newton``, without a derivative: compared in ``test_twin.py``, with SciPy's own stopping
  rule.
"""
