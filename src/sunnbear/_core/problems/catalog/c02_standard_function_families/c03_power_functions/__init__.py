"""This category holds the power function ``x^p`` with a power that need not be a positive integer.

Such a power gives what no polynomial has: a root function with an infinite slope, a zero that is flat to a
fractional order, the edge of a function's domain, and a pole.

The category has 2 kinds of formulas:

- **On ``[-1, 1]``, a signed power:** `SignedPower1` and `SignedPower2` extend ``x^p`` to a negative x as
  ``sign(x)*abs(x)^p``, and differ in how ``c`` enters. `SignedReciprocalPower` does the same for the reciprocal power
  ``x^(-p)``, which changes sign through its pole.
- **On ``[d, 1]``, a power of a positive x:** `NearEdgePower` is ``x^p``, whose domain ends at 0, and `NearPolePower`
  is the reciprocal power, whose pole lies at 0. ``d`` is the distance from 0 to the lower bound of the interval.

Every formula sweeps its power ``p`` over several orders of magnitude, on a logarithmic scale. `helpers` holds what the
formulas share.
"""

from sunnbear._core.problems.core import FormulaCategory

from . import (
    f01_signed_power_1,
    f02_signed_power_2,
    f03_near_edge_power,
    f04_near_pole_power,
    f05_signed_reciprocal_power,
)


class PowerFunctions(FormulaCategory):
    """`PowerFunctions` is the category of power functions with a power that need not be a positive integer."""

    number = (2, 3)
    name = "Power functions"
