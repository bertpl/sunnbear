"""This module holds the float64 constants that several packages share."""

import sys

# `FLOAT64_EPS` is 2^-52, the distance from 1.0 to the next larger float64 value; papers on root finding call it
# ``macheps``, the relative machine precision.
FLOAT64_EPS = sys.float_info.epsilon
# `FLOAT64_MIN` is 2^-1022, the smallest positive float64 value that is not subnormal.
FLOAT64_MIN = sys.float_info.min
# `TINY_LINEAR_TERM_SLOPE` is 2^-918, about 4.5e-277: the slope of the linear term that a modified test problem adds to
# a function that underflows to 0 around its root ``r``.
#
# Because the slope is a power of 2, its product with a float64 value is exact wherever the product is not subnormal:
# ``TINY_LINEAR_TERM_SLOPE*(x - r)`` is exact wherever ``abs(x - r)`` is at least ``FLOAT64_EPS**2``. Adding the term
# changes ``f(x)`` by more than the rounding error of ``f(x)`` only where ``abs(f(x))`` is below
# ``TINY_LINEAR_TERM_SLOPE*abs(x - r)/FLOAT64_EPS``.
TINY_LINEAR_TERM_SLOPE = FLOAT64_MIN / FLOAT64_EPS**2
