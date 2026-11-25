"""This category holds the trigonometric functions sine, cosine and tangent, and the inverse sine and tangent.

The trigonometric functions give behaviors absent from the other families: many roots at equal distances, a root next
to an extremum, close to a double root, and an interval in which roots and poles alternate.

The sine, the cosine and the tangent evaluate their argument at ``0.5*pi*x``, so that their zeros, extrema and poles
lie at integers. A scale of ``x`` beyond that would add nothing: the benchmark's ``xtol`` is a fixed fraction of the
interval's width, so a formula on a wider interval gives the same problem as a steeper formula on a narrower one.

The category has 3 kinds of formulas, which differ in how ``c`` enters:

- **`Sine`, `TangentAcrossPoles` and `InverseTangent` shift ``x`` by ``c``.** The function keeps its form, and ``c``
  moves its roots, its poles or its step.
- **`Cosine` scales ``x`` about the maximum at 0.** A shift of ``x`` would move that maximum and the root next to it
  across the lower bound.
- **`TangentBetweenPoles` and `InverseSine` add ``c`` to the function value.** A shift of ``x`` would move a pole or an
  edge of the domain into the interval. Each divides the function by its value at a bound, so that every candidate of
  the formula has the same c-range.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_sine,
    f02_cosine,
    f03_tangent_between_its_poles,
    f04_tangent_across_its_poles,
    f05_inverse_sine,
    f06_inverse_tangent,
)


class TrigonometricFunctions(FormulaCategory):
    """`TrigonometricFunctions` is the category of the trigonometric functions and their inverses."""

    number = (2, 6)
    name = "Trigonometric functions"
    description = (
        r"The trigonometric functions $\sin$, $\cos$ and $\tan$, and the inverses $\arcsin$ and $\arctan$. The sine "
        r"has many roots at equal distances, the cosine a root close to a maximum, and the tangent poles just outside "
        r"the interval or inside it; $\arcsin$ has an infinite slope at the edges of its domain, and $\arctan$ is a "
        r"step whose tails flatten slowly."
    )
