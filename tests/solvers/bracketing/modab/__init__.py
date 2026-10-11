"""This package tests `ModAB`.

Published results:

- Ganchovski et al. (2026), Table 2: reproduced, in ``test_paper.py``: the roots of all 92 functions, and 89 of the
  92 evaluation counts exactly.
- Ganchovski et al. (2026), Table 1: reproduced, in ``test_paper.py``: the iterations in which `ModAB` switches
  modes, and the iteration in which it stops.
- Ganchovski and Traykov (2023), Table 2: not reproduced, because it describes an earlier version of the method,
  which `ModAB` does not implement.

Reference implementations:

- None: pymodab wraps the authors' compiled library, whose only Linux build is for x86-64, and the tests run on
  ARM.
"""
