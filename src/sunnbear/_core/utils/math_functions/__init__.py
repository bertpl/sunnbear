"""This package holds the real functions that a formula may call besides those of `math`, which numba compiles too.

numba compiles each of them when it compiles a formula that calls it; called from Python, they run as plain Python
when numba's JIT is disabled.
"""

from .bessel import bessel_j0, bessel_j1, bessel_y0, bessel_y1
from .elementary import real_root, sign

__all__ = ["bessel_j0", "bessel_j1", "bessel_y0", "bessel_y1", "real_root", "sign"]
