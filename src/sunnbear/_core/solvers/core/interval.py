"""`Interval` is a `BracketingSolver`'s bracket, reduced step by step; its 2 subclasses are the 2 orientations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property


# ==================================================================================================
#  Interval
# ==================================================================================================
@dataclass(frozen=True)
class Interval(ABC):
    """An `Interval` is a bracket ``[a, b]`` whose endpoint values ``fa`` and ``fb`` differ in sign, or one is zero.

    The orientation is the class: an `IncreasingInterval` holds ``fa <= 0 <= fb`` and a
    `DecreasingInterval` holds ``fa >= 0 >= fb``. Each subclass's name describes its sign change,
    not monotonicity.

    `from_endpoints` picks the class from the values, so a bracketing solver written on `split_at`
    and `root` works for either orientation without checking it; a solver that relies on one
    orientation reads the class.

    Arithmetic on `CountedFloat` endpoints is counted, so interval bookkeeping contributes to a
    solver's flop counts; the invariant checks run on plain floats and cost the solver nothing.
    """

    a: float
    b: float
    fa: float
    fb: float

    def __post_init__(self) -> None:
        """Reject a bracket that is reversed or whose endpoint values do not hold this orientation."""
        if not float(self.a) < float(self.b):
            raise ValueError(f"Interval must satisfy a < b (got a={self.a}, b={self.b}).")
        if not self.is_oriented(float(self.fa), float(self.fb)):
            raise ValueError(
                f"{type(self).__name__} must satisfy {self.orientation_description()} (got fa={self.fa}, fb={self.fb})."
            )

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @staticmethod
    def from_endpoints(a: float, b: float, fa: float, fb: float) -> "Interval":
        """Return the interval matching the endpoint values' orientation.

        Raises:
            ValueError: If ``a >= b``, or ``fa`` and ``fb`` have the same sign and neither is zero.
        """
        fa_plain, fb_plain = float(fa), float(fb)
        if IncreasingInterval.is_oriented(fa_plain, fb_plain):
            return IncreasingInterval(a, b, fa, fb)
        elif DecreasingInterval.is_oriented(fa_plain, fb_plain):
            return DecreasingInterval(a, b, fa, fb)
        else:
            raise ValueError(f"Endpoint values must differ in sign or one must be zero (got fa={fa}, fb={fb}).")

    # --------------------------------------------------------------------------
    #  Orientation
    # --------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def is_oriented(fa: float, fb: float) -> bool:
        """Return whether plain-float endpoint values hold this class's orientation; a solver may ask this too."""

    @staticmethod
    @abstractmethod
    def orientation_description() -> str:
        """Return the orientation as an inequality, for error messages."""

    @abstractmethod
    def _is_on_the_lower_side(self, fx: float) -> bool:
        """Return whether ``fx`` has the sign of ``fa`` or is zero, so the point it came from can replace ``a``."""

    # --------------------------------------------------------------------------
    #  Geometry
    # --------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------
    #  Reduction
    # --------------------------------------------------------------------------
    def split_at(self, x: float, fx: float) -> "Interval":
        """Split the bracket at ``x`` and return the part that still holds the sign change, of the same orientation.

        ``x`` must lie strictly inside the bracket; an ``fx`` of the sign of ``fa``, or zero, makes
        ``x`` the new lower endpoint, otherwise the new upper endpoint.
        """
        if self._is_on_the_lower_side(fx):
            return type(self)(x, self.b, fx, self.fb)
        else:
            return type(self)(self.a, x, self.fa, fx)

    def is_converged(self, doubled_xtol: float) -> bool:
        """Return whether a stopping criterion holds: the width is at most ``doubled_xtol`` or an endpoint is zero.

        The parameter is the doubled tolerance, so the caller computes it once
        per solve, not once per iteration.
        """
        return self.width <= doubled_xtol or self.is_fa_zero or self.is_fb_zero

    def root(self) -> float:
        """Return the best root estimate without another step: a zero endpoint if there is one, else the midpoint."""
        if self.is_fa_zero:
            return self.a
        elif self.is_fb_zero:
            return self.b
        else:
            return self.midpoint


# ==================================================================================================
#  The two orientations
# ==================================================================================================
@dataclass(frozen=True)
class IncreasingInterval(Interval):
    """An `IncreasingInterval` is a bracket with ``fa <= 0 <= fb``: f rises through zero from ``a`` to ``b``."""

    @staticmethod
    def is_oriented(fa: float, fb: float) -> bool:
        """Return whether ``fa <= 0 <= fb``."""
        return fa <= 0.0 <= fb

    @staticmethod
    def orientation_description() -> str:
        """Return ``fa <= 0 <= fb``."""
        return "fa <= 0 <= fb"

    def _is_on_the_lower_side(self, fx: float) -> bool:
        """Return whether ``fx`` is non-positive."""
        return fx <= 0.0


@dataclass(frozen=True)
class DecreasingInterval(Interval):
    """A `DecreasingInterval` is a bracket with ``fa >= 0 >= fb``: f falls through zero from ``a`` to ``b``."""

    @staticmethod
    def is_oriented(fa: float, fb: float) -> bool:
        """Return whether ``fa >= 0 >= fb``."""
        return fa >= 0.0 >= fb

    @staticmethod
    def orientation_description() -> str:
        """Return ``fa >= 0 >= fb``."""
        return "fa >= 0 >= fb"

    def _is_on_the_lower_side(self, fx: float) -> bool:
        """Return whether ``fx`` is non-negative."""
        return fx >= 0.0
