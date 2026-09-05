"""`Interval` is the bracketing state a `BracketingSolver` reduces step by step."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Interval:
    """A bracket ``[a, b]`` with its endpoint values ``fa`` and ``fb``, holding the sign change ``fa <= 0 <= fb``.

    `Solver.solve` normalizes the function's sign before the first step, so
    the invariant is one-directional and every bracketing solver may rely on
    it. Arithmetic on `CountedFloat` endpoints is counted, which is how
    interval bookkeeping lands in a solver's flop counts; the invariant check
    runs on plain floats and costs the solver nothing.
    """

    a: float
    b: float
    fa: float
    fb: float

    def __post_init__(self) -> None:
        """Reject a bracket that is reversed or does not hold the normalized sign change."""
        if not float(self.a) < float(self.b):
            raise ValueError(f"Interval must satisfy a < b (got a={self.a}, b={self.b}).")
        if not float(self.fa) <= 0.0 <= float(self.fb):
            raise ValueError(f"Interval must satisfy fa <= 0 <= fb (got fa={self.fa}, fb={self.fb}).")

    @property
    def width(self) -> float:
        """Return ``b - a``."""
        return self.b - self.a

    @property
    def midpoint(self) -> float:
        """Return the midpoint of the bracket."""
        return 0.5 * (self.a + self.b)

    def replace(self, x: float, fx: float) -> "Interval":
        """Return the half of the bracket that keeps the sign change once ``x`` splits it.

        ``x`` must lie strictly inside the bracket; a non-positive ``fx`` makes
        ``x`` the new lower endpoint, a positive one the new upper endpoint.
        """
        if fx <= 0.0:
            return Interval(x, self.b, fx, self.fb)
        return Interval(self.a, x, self.fa, fx)

    def is_converged(self, two_xtol: float) -> bool:
        """Return whether a stopping criterion holds: the width is at most ``two_xtol``, or an endpoint value is zero.

        Takes the doubled tolerance so the caller computes it once per solve
        instead of once per iteration.
        """
        return self.width <= two_xtol or self.fa == 0.0 or self.fb == 0.0

    def root(self) -> float:
        """Return the root estimate of a converged bracket: the zero endpoint if there is one, else the midpoint."""
        if self.fa == 0.0:
            return self.a
        if self.fb == 0.0:
            return self.b
        return self.midpoint
