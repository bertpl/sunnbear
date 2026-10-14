"""This package tests `Bisection`.

Published results:

- None: bisection is a classical method with no paper of its own.

Third-party published results:

- Atkinson (1989), Table 2.1: reproduced, in ``test_paper.py``: the midpoints ``c_1`` to ``c_15`` and the function
  values of ``c_1`` to ``c_14``, to the printed digits.
- Press et al. (2007), section 9.1.1: no numerical results.
- Chandrupatla (1997), Table 2, and Ganchovski et al. (2026), Table 2, the bisection columns: not checked.

Reference implementations:

- SciPy's ``scipy.optimize.bisect``: compared in ``test_twin.py``.
"""
