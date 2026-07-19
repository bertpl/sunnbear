"""Test-suite configuration.

NUMBA_JIT_COVERAGE makes numba report *compiled* lines to the active coverage
collector, so ``@njit`` function bodies (invisible to coverage.py otherwise)
count once they are compiled on first call. Note the deliberately weaker
standard this implies: compiled means the whole body is marked covered,
regardless of which branches inside it actually executed. Acceptable here
because the jitted population is essentially test-function bodies whose
behavior is asserted by value; plain-Python code is still measured per
executed line. Set before any numba import — numba reads it at import time.
"""

import os

os.environ["NUMBA_JIT_COVERAGE"] = "1"
