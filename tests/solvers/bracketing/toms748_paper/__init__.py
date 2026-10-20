"""This package tests `TOMS748Paper`, for both ``k``: Algorithm 4.1 (``k = 1``) and Algorithm 4.2 (``k = 2``).

The published results come from runs that stop by the termination test of the paper's section 6, so ``test_paper.py``
runs a test-only subclass of `TOMS748Paper` with that test, and passes the paper's tolerance ``tol`` as ``xtol``.

Published results:

- The authors' test output, the roots of all 154 problems of the paper's Table I at ``tol = 0``: reproduced, in
  ``test_paper.py``, for both ``k``: 153 of the 154 roots, within the 14 digits that the output prints. The authors
  produced the output with Algorithm 4.2.
- Alefeld, Potra and Shi (1995), Table II, the columns "4.1" and "4.2": reproduced, in ``test_paper.py``: at each of
  the paper's 4 tolerances, the total evaluation count over the 154 problems lies within 1.2 % of the paper's for
  ``k = 1``, and within 0.4 % for ``k = 2``. At ``tol = 10^-7``, ``10^-10``, ``10^-15`` and 0, the totals are:

  - for ``k = 1``: 2687, 2824, 2901 and 2918, against the paper's 2696, 2835, 2908 and 2950;
  - for ``k = 2``: 2644, 2779, 2856 and 2880, against the paper's 2650, 2786, 2859 and 2884.
- Alefeld, Potra and Shi (1995), Tables IV to VI, the columns "4.1" and "4.2", at ``tol = 10^-15``: reproduced, in
  ``test_paper.py``: for ``k = 1``, 14 of the 17 counts exactly, 1 within 1 and 1 within 2; for ``k = 2``, 15 of the
  17 exactly and 1 within 1. The count of problem ``26[n=1]`` is not checked for either ``k``.

Allowed deviations:

- Problem ``26[n=1]``, the paper's problem 13: its function is 0 on the interval around its root 0 where
  ``exp(1 / x^2)`` overflows, and the solve ends at the first x-value of that interval that it evaluates. That x-value
  differs from the root of the authors' test output, so the test checks that the function is 0 there; the test data
  states why its counts in Tables IV to VI are not checked.
- The totals of Table II all lie below the paper's, for a cause not known. With the paper's machine precision,
  1.9073486328e-16, in place of 2^-52, the totals change by at most 4, so that precision does not explain the
  difference.
- The 3 counts of Tables IV to VI that deviate: the test data states why each deviates.

Published results not used:

- Alefeld, Potra and Shi (1995), Table III: not compared, because the paper does not list the 139 problems behind its
  totals.
- Alefeld, Potra and Shi (1995), the orders of convergence and the efficiency indices of its sections 4 and 5: not
  compared, because they describe the method near a simple root in exact arithmetic, not a run that the paper reports.

Third-party published results:

- None compared.

Reference implementations:

- None: `TOMS748Paper` implements the paper's text, and the tests validate it against the paper's published results
  and the authors' published test output.
"""
