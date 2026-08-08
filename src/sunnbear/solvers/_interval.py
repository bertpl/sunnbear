"""Minimal bracketing state: an interval with its endpoint function values.

The invariant ``fa <= 0 <= fb`` is established once by the solve template
(sign normalization), so every bracketing solver can rely on it. On
`CountedFloat` endpoints the arithmetic in `width` / `midpoint` / `replace`
is flop-counted automatically.
"""

from dataclasses import dataclass


# ==================================================================================================
#  Interval
# ==================================================================================================
@dataclass(frozen=True)
class Interval:
    """A sign-changing bracket ``[a, b]`` with ``fa = f(a) <= 0 <= f(b) = fb``."""

    a: float
    b: float
    fa: float
    fb: float

    def __post_init__(self) -> None:
        """Validate ordering and the sign invariant."""
        if not self.a < self.b:
            raise ValueError(f"Interval requires a < b (got [{self.a}, {self.b}]).")
        if not (self.fa <= 0.0 <= self.fb):
            raise ValueError(f"Interval requires fa <= 0 <= fb (got fa={self.fa}, fb={self.fb}).")

    # --------------------------------------------------------------------------
    #  Derived quantities
    # --------------------------------------------------------------------------
    @property
    def width(self) -> float:
        """Return the interval width ``b - a``."""
        return self.b - self.a

    @property
    def midpoint(self) -> float:
        """Return the interval midpoint ``(a + b) / 2``."""
        return (self.a + self.b) / 2.0

    # --------------------------------------------------------------------------
    #  Reduction
    # --------------------------------------------------------------------------
    def replace(self, x: float, fx: float) -> "Interval":
        """Return the sub-bracket keeping the sign change after evaluating ``f(x) = fx``.

        `x` must lie strictly inside the interval; it replaces the endpoint
        whose function value shares the sign of `fx` (a non-positive `fx`
        replaces `a`, a positive one replaces `b`).
        """
        if fx <= 0.0:
            return Interval(a=x, b=self.b, fa=fx, fb=self.fb)
        return Interval(a=self.a, b=x, fa=self.fa, fb=fx)
