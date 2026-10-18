"""This package tests `ModAB`.

The paper's runs stop by the stopping criterion of its C# code, at the tolerances of its benchmark, so
``test_paper.py`` reproduces Tables 1 and 2 with a test-only subclass of `ModAB` that stops by that criterion and
returns the C# code's x-value ``x3``.

Published results:

- Ganchovski et al. (2026), Table 2: reproduced, in ``test_paper.py``: the roots of all 92 functions, and 89 of the
  92 evaluation counts exactly; the test data states why the other 3 deviate.
- Ganchovski et al. (2026), Table 1: reproduced, in ``test_paper.py``: the iterations in which `ModAB` switches
  modes, and the iteration in which it stops.
- Ganchovski et al. (2026), Table 3, and the rows of Tables 1 and 2 for the method's first version: not compared.
  Table 3 gives execution times of the authors' .NET code, and `ModAB` does not implement the first version.
- Ganchovski and Traykov (2023), Table 2: not reproduced, because it describes an earlier version of the method,
  which `ModAB` does not implement.

Third-party published results:

- None.

Reference implementations:

- None: pymodab wraps the authors' compiled library, whose only Linux build is for x86-64, and the tests run on
  ARM.
"""
