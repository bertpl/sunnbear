"""This category holds the hyperbolic functions ``sinh``, ``cosh`` and ``tanh``, and their inverses.

The hyperbolic functions give 2 behaviors that no polynomial or power function gives: growth as an exponential, and,
for ``tanh``, a function that is close to a step.

Each formula is the plain function on an interval that a parameter sets. A scale of ``x`` would add nothing: the
benchmark's ``xtol`` is a fixed fraction of the interval's width, so ``sinh(s*x)`` on ``[-1, 1]`` and ``sinh(x)`` on
``[-s, s]`` are the same problem for every solver, up to rounding.

The category has 2 kinds of formulas, which differ in how ``c`` enters:

- **`HyperbolicSine`, `HyperbolicCosine` and `HyperbolicTangent` shift ``x`` by ``c``.** The function keeps its form,
  and ``c`` changes the values at the bounds or, for ``tanh``, where the step lies.
- **`InverseHyperbolicSine`, `InverseHyperbolicCosine` and `InverseHyperbolicTangent` add ``c`` to the function
  value.** A shift of ``x`` would move the edge of ``acosh``'s domain and the poles of ``atanh`` into the interval.
  Each divides the function by its value at a bound, so that every candidate of a formula has the same c-range.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_hyperbolic_sine,
    f02_hyperbolic_cosine,
    f03_hyperbolic_tangent,
    f04_inverse_hyperbolic_sine,
    f05_inverse_hyperbolic_cosine,
    f06_inverse_hyperbolic_tangent,
)


class HyperbolicFunctions(FormulaCategory):
    """`HyperbolicFunctions` is the category of the hyperbolic functions and their inverses."""

    number = (2, 4)
    name = "Hyperbolic functions"
