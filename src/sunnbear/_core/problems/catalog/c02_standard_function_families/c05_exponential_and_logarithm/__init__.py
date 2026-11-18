"""This category holds the exponential function and the logarithm.

The exponential function is nearly flat for large negative ``x`` and grows fast for large positive ``x``, and the
logarithm is steep next to its singularity at 0 and flat away from it.

Each formula is the plain function, and a parameter sets its interval. A scale of ``x`` would add nothing: the
benchmark's ``xtol`` is a fixed fraction of the interval's width, so ``exp(s*x)`` on ``[-1, 1]`` and ``exp(x)`` on
``[-s, s]`` are the same problem for every solver, up to rounding.

The 2 formulas differ in how ``c`` enters:

- **`Exponential` shifts ``x`` by ``c``.** The function keeps its form, and ``c`` moves the root between the flat part
  and the steep part.
- **`Logarithm` adds ``c`` to the function value.** A shift of ``x`` would move the singularity into the interval.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import f01_exponential, f02_logarithm


class ExponentialAndLogarithm(FormulaCategory):
    """`ExponentialAndLogarithm` is the category of the exponential function and the logarithm."""

    number = (2, 5)
    name = "Exponential and logarithm"
