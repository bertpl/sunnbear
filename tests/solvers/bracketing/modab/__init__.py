"""This package tests `ModAB` and `ModABSafeguarded`.

The published runs of both methods stop by the stopping criterion of their C# code, at the tolerances of their
benchmarks, so ``test_paper.py`` reproduces their tables with test-only subclasses of both classes that stop by that
criterion and return the C# code's x-value ``x3``.

Published results:

- Ganchovski et al. (2026), Table 2: reproduced by `ModAB`, in ``test_paper.py``: the roots of all 92 functions, and
  89 of the 92 evaluation counts exactly; the test data states why the other 3 deviate.
- Ganchovski et al. (2026), Table 1: reproduced by `ModAB`, in ``test_paper.py``: the iterations in which `ModAB`
  switches modes, and the iteration in which it stops.
- Ganchovski et al. (2026), Table 3, and the rows of Tables 1 and 2 for the method's first version: not compared.
  Table 3 gives execution times of the authors' .NET code, and `ModAB` does not implement the first version.
- Ganchovski and Traykov (2023), Table 2: not reproduced, because it describes an earlier version of the method,
  which `ModAB` does not implement.
- Tomov and Ganchovski (2026), Table 3: reproduced by `ModABSafeguarded`, in ``test_paper.py``, where test-only
  subclasses set B, the factor of the fallback threshold, and M, the largest number of residual exceptions in a row
  (Anderson-Björck steps that continue although the interval shrank too slowly), to
  the 2 settings of the table that differ from `ModABSafeguarded`'s own:

  - all 24 evaluation counts of its 8 cases under its 3 settings, exactly;
  - its sums over the 86 non-stress cases whose returned x-value the authors validated, exactly. Its other 3 sums
    are not compared, because each includes f100, whose function is infinite at its lower bound, which sunnbear
    rejects.
- Tomov and Ganchovski (2026), Table 4: the row "Cap M = 3" reproduced by `ModABSafeguarded`, in
  ``test_paper.py``: the evaluation count, and the returned x-value and final width that the preprint's Section 7.4
  prints. The row "Unlimited exceptions" is not compared, because it runs a version of the C# code that puts no bound
  M on residual exceptions, and that ends at the iteration limit that `ModABSafeguarded` leaves out.
- Tomov and Ganchovski (2026), Table 5: reproduced by `ModABSafeguarded`, in ``test_paper.py``: the returned
  x-values of its 3 cases under each setting of Table 3, and their total evaluation count, which the preprint's
  Section 7.3 gives.
- Tomov and Ganchovski (2026), Proposition 3.6 and Section 7.4: reproduced by `ModABSafeguarded`, in
  ``test_steps.py``: the first 2 secant zeros on the preprint's equation 27, and the fallback after the sixth
  Anderson-Björck step.
- Tomov and Ganchovski (2026), the residuals and widths that Section 7.3 prints for the first Anderson-Björck phases
  of f64 and f84: not compared, because Table 3 already checks the evaluation counts of both solves.
- Tomov and Ganchovski (2026), Proposition 3.5: not compared, because in Proposition 3.5 the Anderson-Björck phase
  continues without a fallback to bisection, while `ModABSafeguarded` falls back.

Third-party published results:

- None.

Reference implementations:

- None: pymodab wraps the authors' compiled library, whose only Linux build is for x86-64, and the tests run on
  ARM.
"""
