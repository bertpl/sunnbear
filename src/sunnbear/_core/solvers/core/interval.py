"""`Interval` is a `BracketingSolver`'s bracketing interval, reduced step by step; a subclass per orientation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import cached_property


# ==================================================================================================
#  IntervalBound
# ==================================================================================================
class IntervalBound(Enum):
    """`IntervalBound` names one of the 2 bounds of an `Interval`: the lower one, ``a``, or the upper one, ``b``."""

    LOWER = "lower"
    UPPER = "upper"


# ==================================================================================================
#  Interval
# ==================================================================================================
@dataclass(frozen=True)
class Interval(ABC):
    """An `Interval` is a bracketing interval ``[a, b]``: the function values at its bounds differ in sign.

    One of them may be zero. The orientation is the class: an `IncreasingInterval` holds ``fa <= 0 <= fb`` and a
    `DecreasingInterval` holds ``fa >= 0 >= fb``. Each subclass's name describes its sign change,
    not monotonicity.

    `from_interval_bounds` picks the class from the values and is the only place that validates them: the
    constructors trust their caller, since every interval is built by the framework, through the
    factory or `split_at`. A bracketing solver written on `split_at` and `root` works for either
    orientation without checking it; a solver that relies on one orientation checks the interval's class.

    Arithmetic and comparisons on `CountedFloat` interval bounds are counted, so interval bookkeeping
    contributes to a solver's flop counts.

    Attributes:
        last_replaced_bound: Which bound the split that produced this interval replaced, or ``None`` for
            the initial interval. A solver reads it to learn which side kept the sign change without
            comparing bounds: the other bound of the interval it split is the one that was discarded.
    """

    a: float
    b: float
    fa: float
    fb: float
    last_replaced_bound: IntervalBound | None = None

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @staticmethod
    def from_interval_bounds(a: float, b: float, fa: float, fb: float) -> "Interval":
        """Return the interval matching the orientation of the function values at its interval bounds.

        When ``fa`` and ``fb`` are both zero, either orientation holds; this returns an `IncreasingInterval`.
        ``a < b`` is the caller's responsibility.

        Raises:
            ValueError: If ``fa`` and ``fb`` have the same sign and neither is zero.
        """
        if fa <= 0.0 <= fb:
            return IncreasingInterval(a, b, fa, fb)
        elif fa >= 0.0 >= fb:
            return DecreasingInterval(a, b, fa, fb)
        else:
            raise ValueError(
                f"The function values at the interval bounds must differ in sign or one must be zero "
                f"(got fa={fa}, fb={fb})."
            )

    # --------------------------------------------------------------------------
    #  Orientation
    # --------------------------------------------------------------------------
    @abstractmethod
    def _has_fa_sign(self, fx: float) -> bool:
        """Return whether ``fx`` has the sign of ``fa`` or is zero."""

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
        """Return the midpoint of the interval."""
        return 0.5 * (self.a + self.b)

    @cached_property
    def is_fa_zero(self) -> bool:
        """Return whether the lower interval bound is an exact root."""
        return self.fa == 0.0

    @cached_property
    def is_fb_zero(self) -> bool:
        """Return whether the upper interval bound is an exact root."""
        return self.fb == 0.0

    # --------------------------------------------------------------------------
    #  Reduction
    # --------------------------------------------------------------------------
    def split_at(self, x: float, fx: float) -> "Interval":
        """Split the interval at ``x`` and return the part that still holds the sign change, of the same orientation.

        ``x`` must lie strictly inside the interval; it replaces ``a`` when `_has_fa_sign` holds for
        ``fx``, else ``b``.
        """
        if self._has_fa_sign(fx):
            return type(self)(x, self.b, fx, self.fb, IntervalBound.LOWER)
        else:
            return type(self)(self.a, x, self.fa, fx, IntervalBound.UPPER)

    def is_converged(self, doubled_xtol: float) -> bool:
        """Return whether a stopping criterion holds: the width is at most ``doubled_xtol`` or a bound value is zero.

        The parameter is the doubled tolerance, so the caller computes it once
        per solve, not once per iteration.
        """
        return self.width <= doubled_xtol or self.is_fa_zero or self.is_fb_zero

    def root(self) -> float:
        """Return the best root estimate without another step: a bound with a zero value if any, else the midpoint."""
        if self.is_fa_zero:
            return self.a
        elif self.is_fb_zero:
            return self.b
        else:
            return self.midpoint


# ==================================================================================================
#  The 2 orientations
# ==================================================================================================
@dataclass(frozen=True)
class IncreasingInterval(Interval):
    """An `IncreasingInterval` is an interval with ``fa <= 0 <= fb``: not positive at ``a``, not negative at ``b``."""

    def _has_fa_sign(self, fx: float) -> bool:
        """Return whether ``fx`` is non-positive."""
        return fx <= 0.0


@dataclass(frozen=True)
class DecreasingInterval(Interval):
    """A `DecreasingInterval` is an interval with ``fa >= 0 >= fb``: not negative at ``a``, not positive at ``b``."""

    def _has_fa_sign(self, fx: float) -> bool:
        """Return whether ``fx`` is non-negative."""
        return fx >= 0.0
