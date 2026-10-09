"""This module holds the float64 constants that several packages share."""

import sys

# `FLOAT64_EPS` is 2^-52, the spacing of float64 values at 1; papers on root finding call it ``macheps``, the
# relative machine precision.
FLOAT64_EPS = sys.float_info.epsilon
