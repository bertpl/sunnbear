"""`Interval` is a `BracketingSolver`'s bracket, reduced step by step."""

from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class Interval:
    """An `Interval` is a bracket ``[a, b]`` with endpoint values ``fa`` and ``fb`` such that ``fa <= 0 <= fb``.

    `Solver.solve` enforces this orientation on the caller's function before an `Interval` is ever
    built, so the invariant is one-directional and every bracketing solver may rely on it.
    Arithmetic on `CountedFloat` endpoints is counted, so interval bookkeeping contributes to a
    solver's flop counts; the invariant check runs on plain floats and costs the solver nothing.
    """

    a: float
    b: float
    fa: float
    fb: float

    def __post_init__(self) -> None:
        """Reject a bracket that is reversed or does not hold ``fa <= 0 <= fb``."""
        if not float(self.a) < float(self.b):
            raise ValueError(f"Interval must satisfy a < b (got a={self.a}, b={self.b}).")
        if not float(self.fa) <= 0.0 <= float(self.fb):
            raise ValueError(f"Interval must satisfy fa <= 0 <= fb (got fa={self.fa}, fb={self.fb}).")

    # The derived values are cached: each costs counted arithmetic, and a step reads some of them more than once.
    @cached_property
    def width(self) -> float:
        """Return ``b - a``."""
        return self.b - self.a

    @cached_property
    def midpoint(self) -> float:
        """Return the midpoint of the bracket."""
        return 0.5 * (self.a + self.b)

    @cached_property
    def is_fa_zero(self) -> bool:
        """Return whether the lower endpoint is an exact root."""
        return self.fa == 0.0

    @cached_property
    def is_fb_zero(self) -> bool:
        """Return whether the upper endpoint is an exact root."""
        return self.fb == 0.0

    def split_at(self, x: float, fx: float) -> "Interval":
        """Split the bracket at ``x`` and return the part that still holds the sign change.

        ``x`` must lie strictly inside the bracket; a non-positive ``fx`` makes
        ``x`` the new lower endpoint, a positive one the new upper endpoint.
        """
        if fx <= 0.0:
            return Interval(x, self.b, fx, self.fb)
        else:
            return Interval(self.a, x, self.fa, fx)

    def is_converged(self, doubled_xtol: float) -> bool:
        """Return whether a stopping criterion holds: the width is at most ``doubled_xtol`` or an endpoint is zero.

        The parameter is the doubled tolerance, so the caller computes it once
        per solve, not once per iteration.
        """
        return self.width <= doubled_xtol or self.is_fa_zero or self.is_fb_zero

    def root(self) -> float:
        """Return the root estimate of a converged bracket: the zero endpoint if there is one, else the midpoint."""
        if self.is_fa_zero:
            return self.a
        elif self.is_fb_zero:
            return self.b
        else:
            return self.midpoint
